# Backend Installation
Capstone by team ID:  C241-PS052

for isntaling follow the step here:

install tesseract-ocr
-
`sudo apt-get install tesseract-ocr` <br>
add your tesseract.exe path in main.py `pytesseract.pytesseract.tesseract_cmd = r'[YOUR-PATH-TO-TESSERACT.EXE]'`

import all pip modules needed
-
`pip install firebase-admin`<br>
`pip install google-auth` <br>
`pip install Pillow`<br>
`pip install mysql-connector-python`<br>
`pip install pytesseract`<br>
`pip install tensorflow numpy'`<br>
`pip install fastapi`<br>

inisiation your service.json
-
`cred = credentials.Certificate(r'[YOUR-JSON-PATH]')`<br>
remember this service is confidential don't share the code inside your service

create dependensi
-
use this command in shell or command terminal
`pip install -r requirements.txt`
or 
`pip freeze > requirements.txt`

api test
--
use postman or use fastapi featur for test the api the result will has same output.<br>
do it in your shell or command terminal => `fastapi dev main.py` for development environtment, `fastapi run` for production environtment.<br>
copy on http url and copy to postman and ajust the endPoint for testing, or just click on http://YOUR-URL/docs#/ for test in fastapi featur
