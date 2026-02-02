import streamlit as st
import pandas as pd
from datetime import datetime

from ui.login import auth_ui
from risk_engine import HealthInput, HealthRiskEngine
from database.firestore import (
    save_health_log,
    get_health_logs,
    save_bulk_health_logs
)

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="WellPath – AI HealthBuddy",
    page_icon="🩺",
    layout="centered"
)

# ---------------- AUTH ----------------
if "user" not in st.session_state:
    auth_ui()
    st.stop()

# ---------------- HEADER ----------------
st.markdown("""
# 🩺 WellPath  
### Your AI-powered daily health companion
""")

st.sidebar.markdown(f"👤 **{st.session_state['user']}**")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")

# ---------------- FETCH DATA ----------------
user_logs = get_health_logs(st.session_state["user"], limit=30)

df = None
if user_logs:
    df = pd.DataFrame(user_logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Safe defaults (backward compatibility)
    for col, default in {
        "ai_rule_disagree": False,
        "ml_risk_label": None,
        "ml_risk_probability": None
    }.items():
        if col not in df.columns:
            df[col] = default

# ================== DASHBOARD ==================

# -------- RISK TREND --------
if df is not None and len(df) > 1:
    st.subheader("📈 Risk Score Trend")
    st.line_chart(df.set_index("timestamp")[["risk_score"]])

# -------- DISAGREEMENT TREND --------
if df is not None:
    st.subheader("🧠 AI vs Rule Disagreement Trend")
    st.area_chart(df.set_index("timestamp")[["ai_rule_disagree"]])

# -------- HISTORY TABLE --------
st.subheader("📊 Health History")
if df is not None:
    st.dataframe(
        df[[
            "timestamp",
            "risk_score",
            "stress",
            "sleep",
            "weight",
            "ml_risk_label",
            "ai_rule_disagree"
        ]],
        use_container_width=True
    )
else:
    st.info("No health data yet.")

# ================== INSIGHTS ==================
st.subheader("🧠 Health Insights")

if df is not None and len(df) >= 3:
    recent = df.tail(3)

    if recent["risk_score"].iloc[-1] > recent["risk_score"].iloc[0]:
        st.warning("🔴 Risk is increasing recently.")
    else:
        st.success("🟢 Risk is stable or improving.")

    if recent["stress"].mean() >= 7:
        st.warning("⚠️ High stress detected.")
    if recent["sleep"].mean() < 6:
        st.warning("💤 Low sleep duration detected.")

# ================== HEALTH CHANGE ==================
from analysis.health_trends import compute_health_change

st.subheader("📉 Health Change Summary")
change_score = compute_health_change(df)

if change_score is None:
    st.info("Not enough data.")
elif change_score > 0:
    st.error(f"⚠️ Health risk increased by {change_score} points.")
elif change_score < 0:
    st.success(f"✅ Health risk improved by {abs(change_score)} points.")
else:
    st.info("➖ No major change detected.")

# ================== CORRELATION ==================
st.subheader("🔍 What’s affecting your risk?")
if df is not None and len(df) >= 5:
    corr = df[["risk_score", "stress", "sleep"]].corr()
    if corr.loc["risk_score", "stress"] > 0.4:
        st.warning("📈 Stress strongly increases risk.")
    if corr.loc["risk_score", "sleep"] < -0.4:
        st.warning("💤 Better sleep reduces risk.")

# ================== SIMULATION ==================
with st.expander("🧪 Simulation & Testing Tools"):
    from simulation.health_simulator import generate_health_logs

    col1, col2 = st.columns(2)
    with col1:
        pattern = st.selectbox("Pattern", ["worsening", "improving"])
    with col2:
        days = st.slider("Days", 7, 60, 30)

    if st.button("🚀 Generate Simulated Data"):
        logs = generate_health_logs(days=days, base_age=25, pattern=pattern)
        save_bulk_health_logs(st.session_state["user"], logs)
        st.success("Simulation data added.")
        st.rerun()

# ================== MODEL TRAINING ==================
with st.expander("🤖 Model Training"):
    if st.button("Train Personal Model"):
        from ml.dataset_builder import build_dataset
        from ml.train_model import train_risk_model

        if df is None or len(df) < 20:
            st.warning("Need at least 20 logs.")
        else:
            acc = train_risk_model(build_dataset(user_logs))
            st.success(f"Model trained. Accuracy: {acc}%")

    if st.button("Train Using Medical Dataset"):
        from ml.external_dataset_adapter import load_heart_dataset
        from ml.train_external_model import train_from_external_data

        X, y = load_heart_dataset("data/heart.csv")
        acc = train_from_external_data(X, y)
        st.success(f"Medical model trained. Accuracy: {acc}%")

# ================== INPUT FORM ==================
st.markdown("## 🧾 Today’s Health Check")

with st.container(border=True):
    with st.form("health_form"):
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", 1, 120, 25)
            weight = st.number_input("Weight (kg)", 20.0, 300.0, 70.0)
        with c2:
            stress = st.slider("Stress Level", 1, 10, 5)
            sleep = st.slider("Sleep Hours", 0.0, 12.0, 7.0)

        urine = st.selectbox("Urine Frequency", ["normal", "increased"])
        symptoms = st.multiselect(
            "Symptoms",
            [
                "fatigue", "fever", "chest_pain",
                "shortness_of_breath", "dizziness",
                "frequent_urination"
            ]
        )

        submitted = st.form_submit_button("🧠 Assess My Health")

# ================== RISK ASSESSMENT ==================
if submitted:
    engine = HealthRiskEngine()
    result = engine.assess_risk(
        HealthInput(age, weight, stress, sleep, urine, symptoms)
    )

    from ml.predictor import predict_risk
    ml_prob, ml_label = predict_risk(
        age=age,
        cholesterol=200,
        stress=stress,
        sleep=sleep,
        urine=0
    )

    ai_rule_disagree = result["risk_level"] != ml_label

    # -------- METRICS --------
    st.subheader("⚖️ Risk Comparison")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rule Risk", result["risk_level"])
    c2.metric("AI Risk", ml_label)
    c3.metric("AI Probability", f"{ml_prob}%")

    if ai_rule_disagree:
        st.warning("⚠️ AI and rules disagree — monitor closely.")
    else:
        st.success("✅ AI and rules agree.")

    # -------- SAVE --------
    save_health_log(
        st.session_state["user"],
        {
            "timestamp": datetime.utcnow(),
            "age": age,
            "weight": weight,
            "stress": stress,
            "sleep": sleep,
            "urine": urine,
            "symptoms": symptoms,
            "risk_level": result["risk_level"],
            "risk_score": result["risk_score"],
            "recommended_action": result["recommended_action"],
            "ml_risk_label": ml_label,
            "ml_risk_probability": ml_prob,
            "ai_rule_disagree": ai_rule_disagree
        }
    )

    st.success("Health log saved successfully.")

st.caption("⚠️ This app provides AI-assisted health insights, not medical advice.")

    
     