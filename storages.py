import firebase_admin
from firebase_admin import credentials, storage
import os
import time

# generate firebase nama unik
firebase_app_name = "my_storage_app_" + str(int(time.time()))

cred = credentials.Certificate(r"D:\koding\kode utama\capstone\service.json")

# inisiasi Firebase app dengan unique name
if firebase_app_name not in firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'capstone-63fa5.appspot.com' #nama firebase bucket/nama bucket
    }, name=firebase_app_name)

#upload
def upload_to_storage(file_stream, filename):
    bucket = storage.bucket(app=firebase_admin.get_app(firebase_app_name))
    blob = bucket.blob(filename)
    blob.upload_from_file(file_stream)
    url = blob.public_url
    return url
