def generate_recommendations(df, rule_risk_level, ml_label):
    recommendations = []

    if df is None or len(df) < 2:
        recommendations.append(
            "Log your health daily to unlock personalized recommendations."
        )
        return recommendations

    recent = df.tail(5)

    avg_stress = recent["stress"].mean()
    avg_sleep = recent["sleep"].mean()

    risk_start = recent["risk_score"].iloc[0]
    risk_end = recent["risk_score"].iloc[-1]

    # -------- RISK TREND --------
    if risk_end > risk_start:
        recommendations.append(
            "Your health risk has been increasing recently. Focus on recovery and stress reduction."
        )
    else:
        recommendations.append(
            "Your recent health trend is stable or improving. Keep maintaining these habits."
        )

    # -------- STRESS --------
    if avg_stress >= 7:
        recommendations.append(
            "High stress levels detected. Consider breathing exercises, reduced screen time, or short breaks."
        )
    elif avg_stress >= 5:
        recommendations.append(
            "Moderate stress levels observed. Improving work-life balance may help."
        )

    # -------- SLEEP --------
    if avg_sleep < 6:
        recommendations.append(
            "Consistently low sleep detected. Aim for at least 7–8 hours to support recovery."
        )

    # -------- RISK LEVEL BASED --------
    if rule_risk_level == "HIGH":
        recommendations.append(
            "High overall risk detected. Avoid strenuous activity and consider consulting a healthcare professional."
        )
    elif rule_risk_level == "MEDIUM":
        recommendations.append(
            "Moderate risk detected. Lifestyle improvements can significantly reduce future risk."
        )
    else:
        recommendations.append(
            "Low risk detected. Continue healthy habits and regular monitoring."
        )

    # -------- AI vs RULE DISAGREEMENT --------
    if rule_risk_level != ml_label:
        recommendations.append(
            "AI and rule-based assessments differ. Monitor closely and log more data for clarity."
        )

    return recommendations
