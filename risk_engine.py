from dataclasses import dataclass
from typing import List, Dict

@dataclass
class HealthInput:
    age: int
    weight: float
    stress_level: int       # 1–10
    sleep_hours: float
    urine_frequency: str    # "normal" or "increased"
    symptoms: List[str]     # e.g. ["fatigue", "fever"]

class HealthRiskEngine:
    def __init__(self):
        self.symptom_weights = {
            "fever": 25,
            "fatigue": 15,
            "chest_pain": 40,
            "shortness_of_breath": 40,
            "dizziness": 20,
            "frequent_urination": 20
        }

    def assess_risk(self, data: HealthInput) -> Dict:
        score = 0
        reasons = []

        # Age risk
        if data.age >= 45:
            score += 15
            reasons.append("Age above 45 increases health risk")

        # Stress
        if data.stress_level >= 7:
            score += 15
            reasons.append("High stress levels detected")

        # Sleep
        if data.sleep_hours < 6:
            score += 10
            reasons.append("Insufficient sleep")

        # Urine frequency
        if data.urine_frequency == "increased":
            score += 20
            reasons.append("Increased urination may indicate metabolic issues")

        # Symptoms
        for symptom in data.symptoms:
            if symptom in self.symptom_weights:
                score += self.symptom_weights[symptom]
                reasons.append(f"Symptom reported: {symptom.replace('_', ' ')}")

        # Cap score
        score = min(score, 100)

        # Risk level
        if score < 30:
            risk_level = "LOW"
            action = "Continue monitoring and maintain a healthy lifestyle."
        elif score < 60:
            risk_level = "MEDIUM"
            action = "Consider consulting a general physician within 1–2 weeks."
        else:
            risk_level = "HIGH"
            action = "Seek medical attention as soon as possible."

        return {
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons,
            "recommended_action": action
        }
