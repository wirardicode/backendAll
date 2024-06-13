import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Initialize Firestore DB
cred = credentials.Certificate(r'D:\koding\kode utama\capstone\service.json')
firebase_admin.initialize_app(cred)

db = firestore.client() #koneksi ke firestore default

def save_to_firestore(data):
    try:
        # Menyimpan data ke Firestore
        db.collection('ocr_results').add(data)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    
#utuh
def get_all_documents():
    try:
        # Mendapatkan semua dokumen dari koleksi 'ocr_results'
        docs = db.collection('ocr_results').stream()
        results = [doc.to_dict() for doc in docs]
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

#by document
def get_document_by_id(doc_id):
    try:
        # Mendapatkan dokumen berdasarkan ID
        doc = db.collection('ocr_results').document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None    