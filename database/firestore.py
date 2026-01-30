import firebase_admin
from firebase_admin import credentials, firestore

# Prevent re-initialization error
if not firebase_admin._apps:
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_health_log(user_email, data):
    doc_ref = db.collection("users").document(user_email)
    doc_ref.collection("health_logs").add(data)
