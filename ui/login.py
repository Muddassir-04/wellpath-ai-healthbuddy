import streamlit as st
from auth.firebase_auth import signup, login

def auth_ui():
    st.title("🔐 Login to WellPath")

    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Select option", menu)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    error_placeholder = st.empty()

    if choice == "Sign Up":
        if st.button("Create Account"):
            try:
                signup(email, password)
                st.success("Account created successfully. Please login.")
            except Exception as e:
                error_placeholder.error("Signup failed. Try a stronger password.")

    if choice == "Login":
        if st.button("Login"):
            try:
                user = login(email, password)
                st.session_state["user"] = user["email"]
                st.rerun()  # 🔥 immediate redirect
            except Exception:
                error_placeholder.error("Invalid credentials. Please try again.")
