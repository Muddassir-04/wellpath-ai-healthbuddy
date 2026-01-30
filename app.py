import streamlit as st
from ui.login import auth_ui
from risk_engine import HealthInput, HealthRiskEngine

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="WellPath – AI HealthBuddy",
    page_icon="🩺",
    layout="centered"
)

# ---------------- AUTH GATE ----------------
if "user" not in st.session_state:
    auth_ui()
    st.stop()   # ⛔ Stop here if not logged in

# ---------------- APP UI (ONLY AFTER LOGIN) ----------------
st.title("🩺 WellPath – AI HealthBuddy")
st.caption("Your daily personal health assistant")

st.markdown(f"👤 Logged in as **{st.session_state['user']}**")

if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")

# Sidebar
st.sidebar.header("About")
st.sidebar.info(
    "WellPath helps you monitor your health daily and guides "
    "you on when and how to take action."
)

# ---------------- INPUT FORM ----------------
st.subheader("Enter your health details")

with st.form("health_form"):
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
    stress = st.slider("Stress Level (1 = low, 10 = high)", 1, 10, 5)
    sleep = st.slider("Average Sleep Hours", 0.0, 12.0, 7.0)

    urine = st.selectbox(
        "Urine Frequency",
        ["normal", "increased"]
    )

    symptoms = st.multiselect(
        "Symptoms (if any)",
        [
            "fatigue",
            "fever",
            "chest_pain",
            "shortness_of_breath",
            "dizziness",
            "frequent_urination"
        ]
    )

    submitted = st.form_submit_button("Assess My Health")

# ---------------- RISK ASSESSMENT ----------------
if submitted:
    engine = HealthRiskEngine()

    user_data = HealthInput(
        age=age,
        weight=weight,
        stress_level=stress,
        sleep_hours=sleep,
        urine_frequency=urine,
        symptoms=symptoms
    )

    result = engine.assess_risk(user_data)

    st.markdown("---")
    st.subheader("🧠 Health Assessment Result")

    if result["risk_level"] == "LOW":
        st.success(f"🟢 Risk Level: {result['risk_level']}")
    elif result["risk_level"] == "MEDIUM":
        st.warning(f"🟡 Risk Level: {result['risk_level']}")
    else:
        st.error(f"🔴 Risk Level: {result['risk_level']}")

    st.metric("Risk Score", f"{result['risk_score']} / 100")

    st.markdown("### Why this assessment?")
    for reason in result["reasons"]:
        st.write("•", reason)

    st.markdown("### Recommended Action")
    st.info(result["recommended_action"])

    st.caption(
        "⚠️ This tool does not replace professional medical advice."
    )
