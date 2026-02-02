import streamlit as st

def signup(email, password):
    # For demo/MVP: just accept signup
    return {"email": email}

def login(email, password):
    # For demo/MVP: just log user in
    if email and password:
        st.session_state["user"] = email
        return True
    return False

