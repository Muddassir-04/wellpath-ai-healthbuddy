import streamlit as st
import pandas as pd
from datetime import datetime

from ui.login import auth_ui
from risk_engine import HealthInput, HealthRiskEngine
from database.firestore import save_health_log, get_health_logs, save_bulk_health_logs

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

# ---------------- APP HEADER ----------------
st.title("🩺 WellPath – AI HealthBuddy")
st.caption("Your daily personal health assistant")

st.markdown(f"👤 Logged in as **{st.session_state['user']}**")

if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")

# ---------------- FETCH USER HISTORY ----------------
user_logs = get_health_logs(st.session_state["user"], limit=30)

# ---------------- STEP 2: DATAFRAME ----------------
df = None
if user_logs:
    df = pd.DataFrame(user_logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

# ---------------- HISTORY TABLE ----------------
st.subheader("📊 Your Health History")

if df is not None:
    st.dataframe(
        df[[
            "timestamp",
            "risk_score",
            "stress",
            "sleep",
            "weight"
        ]],
        use_container_width=True
    )
else:
    st.info("No health history found yet. Start logging today!")
    
st.subheader("🧪 Demo & Simulation")

from simulation.health_simulator import generate_health_logs
from database.firestore import save_bulk_health_logs

col1, col2 = st.columns(2)

with col1:
    pattern = st.selectbox(
        "Simulation Pattern",
        ["worsening", "improving"]
    )

with col2:
    days = st.slider("Number of Days", 7, 60, 30)

if st.button("🚀 Generate Simulated Health Data"):
    logs = generate_health_logs(
        days=days,
        base_age=25,
        pattern=pattern
    )

    save_bulk_health_logs(
        st.session_state["user"],
        logs
    )

    st.success(f"✅ {days} days of simulated health data generated!")
    st.rerun()

    
# ---------------- RISK SCORE CHART ----------------
if df is not None and len(df) > 1:
    st.subheader("📈 Risk Score Trend")

    chart_df = df.set_index("timestamp")[["risk_score"]]
    st.line_chart(chart_df)

elif df is not None and len(df) == 1:
    st.info("Add more daily logs to see trends over time.")

# ---------------- HEALTH INSIGHTS ----------------
st.subheader("🧠 Health Insights")

if df is not None and len(df) >= 2:
    insights = []

    # Recent values
    recent = df.tail(3)

    avg_risk = recent["risk_score"].mean()
    avg_stress = recent["stress"].mean()
    avg_sleep = recent["sleep"].mean()

    # ---- Risk trend ----
    if recent["risk_score"].iloc[-1] > recent["risk_score"].iloc[0]:
        insights.append("🔴 Your health risk score is increasing recently.")
    else:
        insights.append("🟢 Your health risk score is stable or improving.")

    # ---- Stress analysis ----
    if avg_stress >= 7:
        insights.append("⚠️ High stress levels detected. Consider relaxation and rest.")
    elif avg_stress >= 5:
        insights.append("🟡 Moderate stress levels. Try improving work-life balance.")
    else:
        insights.append("🟢 Stress levels look healthy.")

    # ---- Sleep analysis ----
    if avg_sleep < 6:
        insights.append("💤 Your sleep duration is consistently low. Aim for 7–8 hours.")
    else:
        insights.append("🟢 Your sleep pattern is within a healthy range.")

    # ---- Display insights ----
    for insight in insights:
        st.info(insight)

elif df is not None:
    st.info("Add more daily logs to unlock health insights.")
else:
    st.info("No health data available yet.")
    
from analysis.health_trends import compute_health_change

st.subheader("📉 Health Change Summary")

change_score = compute_health_change(df)

if change_score is None:
    st.info("Log more days to analyze health changes.")
else:
    if change_score > 0:
        st.error(f"⚠️ Health risk increased by {change_score} points recently.")
    elif change_score < 0:
        st.success(f"✅ Health risk improved by {abs(change_score)} points.")
    else:
        st.info("➖ No significant change detected.")

st.subheader("🔍 What’s affecting your risk?")

if df is not None and len(df) >= 5:
    corr = df[["risk_score", "stress", "sleep"]].corr()

    stress_corr = corr.loc["risk_score", "stress"]
    sleep_corr = corr.loc["risk_score", "sleep"]

    if stress_corr > 0.4:
        st.warning("📈 Higher stress is strongly linked to increased health risk.")
    if sleep_corr < -0.4:
        st.warning("💤 Better sleep is strongly linked to lower health risk.")

st.subheader("🤖 AI Model Training")

if st.button("Train Risk Prediction Model"):
    from ml.dataset_builder import build_dataset
    from ml.train_model import train_risk_model

    if df is None or len(df) < 20:
        st.warning("Not enough data to train ML model (need at least 20 logs).")
    else:
        dataset = build_dataset(user_logs)
        accuracy = train_risk_model(dataset)
        st.success(f"✅ Model trained successfully! Accuracy: {accuracy}%")
        
    st.subheader("🤖 Train AI using Medical Dataset")

if st.button("Train using Public Healthcare Data"):
    from ml.external_dataset_adapter import load_heart_dataset
    from ml.train_external_model import train_from_external_data

    X, y = load_heart_dataset("data/heart.csv")
    acc = train_from_external_data(X, y)

    st.success(f"✅ Model trained using real medical data! Accuracy: {acc}%")



st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("About WellPath")
st.sidebar.info(
    "WellPath helps you monitor your health daily, "
    "track trends, and guides you on when to take action."
)
st.caption(
    "⚠️ AI predictions are probabilistic and for awareness only. "
    "They do not replace clinical diagnosis."
)


# ---------------- INPUT FORM ----------------
st.subheader("🧾 Enter Today’s Health Details")

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

    # -------- RULE-BASED ENGINE --------
    result = engine.assess_risk(user_data)
    rule_risk_level = result["risk_level"]

    # -------- ML PREDICTION --------
    from ml.predictor import predict_risk

    cholesterol = 200  # temporary proxy

    ml_prob, ml_label = predict_risk(
        age=age,
        cholesterol=cholesterol,
        stress=stress,
        sleep=sleep,
        urine=0
    )

    # -------- DISPLAY AI RESULT --------
    st.subheader("🤖 AI Risk Prediction (ML-Based)")
    st.metric("ML Risk Probability", f"{ml_prob}%")

    if ml_label == "HIGH":
        st.error("🔴 AI Model predicts HIGH health risk.")
    else:
        st.success("🟢 AI Model predicts LOW health risk.")

    # -------- COMPARISON --------
    st.subheader("⚖️ Rule-Based vs AI-Based")

    st.write(f"Rule-Based Risk: **{rule_risk_level}**")
    st.write(f"AI-Based Risk: **{ml_label}**")

    if rule_risk_level != ml_label:
        st.warning("AI and rule-based system disagree. Monitor closely.")
    else:
        st.success("Both systems agree on your risk level.")

    # -------- SAVE TO FIRESTORE --------
    
    ai_rule_disagree = rule_risk_level != ml_label
    
    health_record = {
        "timestamp": datetime.utcnow(),

        # user inputs
        "age": age,
        "weight": weight,
        "stress": stress,
        "sleep": sleep,
        "urine": urine,
        "symptoms": symptoms,

        # rule-based
        "risk_level": rule_risk_level,
        "risk_score": result["risk_score"],
        "recommended_action": result["recommended_action"],

        # AI-based (NEW)
        "ml_risk_label": ml_label,
        "ml_risk_probability": ml_prob,
        "ai_rule_disagree": ai_rule_disagree
    }
        
    save_health_log(
        st.session_state["user"],
        health_record
    )
    
    # -------- PERSONALIZED RECOMMENDATIONS --------
    from recommendation.recommender import generate_recommendations

    st.subheader("🧭 Personalized Recommendations")

    recs = generate_recommendations(df, rule_risk_level, ml_label)

    for rec in recs:
        st.info("• " + rec)

    # -------- FINAL RESULT --------
    st.markdown("---")
    st.subheader("🧠 Health Assessment Result")

    if rule_risk_level == "LOW":
        st.success(f"🟢 Risk Level: {rule_risk_level}")
    elif rule_risk_level == "MEDIUM":
        st.warning(f"🟡 Risk Level: {rule_risk_level}")
    else:
        st.error(f"🔴 Risk Level: {rule_risk_level}")

    st.metric("Risk Score", f"{result['risk_score']} / 100")

    st.markdown("### Why this assessment?")
    for reason in result["reasons"]:
        st.write("•", reason)

    st.markdown("### Recommended Action")
    st.info(result["recommended_action"])

    st.caption("⚠️ This tool does not replace professional medical advice.")

    
     