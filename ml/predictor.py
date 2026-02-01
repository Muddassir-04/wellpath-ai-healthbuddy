import pickle
import numpy as np

MODEL_PATH = "ml/external_risk_model.pkl"

def predict_risk(age, cholesterol, stress, sleep, urine):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    X = np.array([[age, cholesterol, stress, sleep, urine]])

    prob = model.predict_proba(X)[0][1]  # probability of high risk
    label = "HIGH" if prob >= 0.5 else "LOW"

    return round(prob * 100, 2), label
