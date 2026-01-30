import pyrebase

firebase_config = {
    "apiKey": "AIzaSyB9nESdLTcGi-PI6XRB3G6IOOel57U7WHI",
  "authDomain": "wellpath-40600.firebaseapp.com",
  "projectId": "wellpath-40600",
  "storageBucket": "wellpath-40600.firebasestorage.app",
  "messagingSenderId": "428503110848",
  "appId": "1:428503110848:web:2292f772ee315df51e4925",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def signup(email, password):
    return auth.create_user_with_email_and_password(email, password)

def login(email, password):
    return auth.sign_in_with_email_and_password(email, password)
