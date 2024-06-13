from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from typing import List, Dict
import model  # This assumes model.py is in the same directory
import dbconn  # Import the dbconn module
#modul for authentication
from firebase_admin import credentials, initialize_app, auth
from google.auth.transport import requests
from google.oauth2 import id_token
#modul for ocr
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import os
import re
from firestore import save_to_firestore,  get_all_documents, get_document_by_id, cred  # Import fungsi dari firestore.py
from storages import upload_to_storage  # Import fungsi dari storages.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Inisialisasi Firebase Admin SDK
#cred = credentials.Certificate(r"D:\koding\kode utama\capstone\service.json")
#initialize_app(cred)

app = FastAPI()

class BudgetRequest(BaseModel):
    income: float

class BudgetResponse(BaseModel):
    primary: float
    secondary: float
    tertiary: float

# mendefinisikan Model Pydantic
class Token(BaseModel):
    token: str

class User(BaseModel):
    uid: str
    email: str
    display_name: str

@app.post("/predict/", response_model=BudgetResponse)
async def predict_budget(request: BudgetRequest):
    try:
        # Predict budget based on income
        categories = ['food', 'family', 'household', 'health', 'self-development', 'education', 'rent','transportation', 'funding', 'life insurance', 'beauty', 'maid', 'money transfer', 'recurring deposit', 'tourism', 'investment','subscription', 'festivals', 'apparel', 'gift', 'culture', 'other']  # Replace with actual categories
        prediction = model.predict_budget(categories, request.income)
        
        # Calculate budget allocation based on prediction
        total = request.income
        primary_budget = total * (0.5 if 'Primary' in prediction else 0)
        secondary_budget = total * (0.3 if 'Secondary' in prediction else 0)
        tertiary_budget = total * (0.2 if 'Tertiary' in prediction else 0)

        # Calculate spending percentages
        total_spending = primary_budget + secondary_budget + tertiary_budget
        primary_percentage = (primary_budget / total_spending) * 100 if total_spending > 0 else 0
        secondary_percentage = (secondary_budget / total_spending) * 100 if total_spending > 0 else 0
        tertiary_percentage = (tertiary_budget / total_spending) * 100 if total_spending > 0 else 0

        # Save to database
        success = dbconn.save_budget_request(
            request.income, primary_percentage, secondary_percentage, tertiary_percentage
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save to database")

        return BudgetResponse(
            primary=primary_percentage,
            secondary=secondary_percentage,
            tertiary=tertiary_percentage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#metode for authentication
@app.post("/verify-token", response_model=User)
async def verify_token(token: Token):
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token.token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)

        return User(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/google-login", response_model=User)
async def google_login(token: Token):
    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(token.token, requests.Request())
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        uid = id_info['sub']
        email = id_info.get('email')
        display_name = id_info.get('name')

        # Use Firebase Admin SDK to create or get the user
        user = auth.get_user_by_email(email)
        if not user:
            user = auth.create_user(uid=uid, email=email, display_name=display_name)

        return User(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
#ocr
@app.post("/ocr")
async def ocr(image: UploadFile = File(...)):
    if not image:
        raise HTTPException(status_code=400, detail="No file part")
    
    if image.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")
    
    try:
        img = Image.open(image.file)
        text = pytesseract.image_to_string(img)

        # Mencari angka di baris terakhir
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        last_line = None
        for line in reversed(lines):
            if any(char.isdigit() for char in line):
                last_line = line
                break
        
        # Mengunggah file ke Cloud Storage
        image.file.seek(0)  # Reset stream position to the beginning
        file_url = upload_to_storage(image.file, image.filename)
        
        if last_line:
            # Mengambil angka dari last_line
            numbers = re.findall(r'\d+', last_line)
            combined_number = ''.join(numbers)  # Menggabungkan angka tanpa koma
            result = {"Money spend": combined_number, "image_url": file_url}
            save_to_firestore(result)  # Simpan hasil ke Firestore
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=404, detail="Number not found sorry")
    except Exception as e:
        raise HTTPException(status_code=500, detail="File processing error")

#mendapatkan semua isi firestore
@app.get("/get-documents")
def read_documents():
    try:
        documents = get_all_documents()
        return {"documents": documents}
    except Exception as e:
        return {"error": str(e)}

#mendapatkan isi firestor dari document ID tertentu
@app.get("/get-document/{doc_id}")
def read_document(doc_id: str):
    try:
        document = get_document_by_id(doc_id)
        if document:
            return {"document": document}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
