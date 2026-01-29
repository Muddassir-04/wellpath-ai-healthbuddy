from risk_engine import HealthInput, HealthRiskEngine

engine = HealthRiskEngine()

user_data = HealthInput(
    age=28,
    weight=82,
    stress_level=8,
    sleep_hours=5,
    urine_frequency="increased",
    symptoms=["fatigue"]
)

result = engine.assess_risk(user_data)

print("Risk Level:", result["risk_level"])
print("Risk Score:", result["risk_score"])
print("Reasons:")
for r in result["reasons"]:
    print("-", r)
print("Action:", result["recommended_action"])
