import random
from datetime import datetime, timedelta


def generate_health_logs(
    days: int = 30,
    base_age: int = 25,
    pattern: str = "worsening"
):
    """
    Generate realistic simulated health logs for demo & ML training
    pattern: 'worsening' or 'improving'
    """

    logs = []
    now = datetime.utcnow()

    # ---------------- BASE VALUES ----------------
    stress = random.randint(4, 6)
    sleep = random.uniform(6.5, 7.5)
    weight = random.uniform(65, 75)

    cholesterol = random.randint(180, 210)
    bp = random.randint(110, 125)
    heart_rate = random.randint(65, 80)

    # Trend direction
    direction = 1 if pattern == "worsening" else -1

    for i in range(days):
        timestamp = now - timedelta(days=(days - i))

        # ---- Gradual drift ----
        stress = min(10, max(1, stress + direction * random.uniform(0.1, 0.4)))
        sleep = min(9, max(4, sleep - direction * random.uniform(0.1, 0.3)))
        weight = min(120, max(40, weight + direction * random.uniform(0.05, 0.2)))

        cholesterol = min(300, max(150, cholesterol + direction * random.randint(1, 4)))
        bp = min(180, max(90, bp + direction * random.randint(1, 3)))
        heart_rate = min(120, max(55, heart_rate + direction * random.randint(1, 2)))

        # ---- Rule-based risk score simulation ----
        risk_score = (
            stress * 6
            + max(0, (7 - sleep)) * 8
            + (cholesterol - 180) * 0.15
            + (bp - 120) * 0.3
        )

        risk_score = int(min(100, max(5, risk_score)))

        # ---- Risk level ----
        if risk_score < 35:
            risk_level = "LOW"
        elif risk_score < 65:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # ---- Symptoms logic ----
        symptoms = []
        if stress > 7:
            symptoms.append("fatigue")
        if sleep < 6:
            symptoms.append("dizziness")
        if bp > 140:
            symptoms.append("chest_pain")

        log = {
            "timestamp": timestamp,
            "age": base_age,
            "weight": round(weight, 1),
            "stress": round(stress, 1),
            "sleep": round(sleep, 1),

            # Medical features
            "cholesterol": cholesterol,
            "blood_pressure": bp,
            "heart_rate": heart_rate,

            # Risk outputs
            "risk_score": risk_score,
            "risk_level": risk_level,

            # Lifestyle
            "exercise": random.choice([0, 1]),
            "urine": random.choice(["normal", "increased"]),
            "symptoms": symptoms,
        }

        logs.append(log)

    return logs
