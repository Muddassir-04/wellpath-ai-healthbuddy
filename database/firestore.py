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

def get_health_logs(user_email, limit=30):
    logs_ref = (
        db.collection("users")
        .document(user_email)
        .collection("health_logs")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )

    docs = logs_ref.stream()

    data = []
    for doc in docs:
        record = doc.to_dict()
        record["id"] = doc.id
        data.append(record)

    return data
