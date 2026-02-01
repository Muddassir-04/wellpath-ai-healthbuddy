import pandas as pd

def load_heart_dataset(path):
    df = pd.read_csv(path)

    # ---- Rename to WellPath-style features ----
    df = df.rename(columns={
        "resting_blood_pressure": "stress",
        "cholestoral": "cholesterol",
        "Max_heart_rate": "sleep"
    })

    # ---- Required columns check ----
    required = ["age", "stress", "cholesterol", "sleep", "target"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ---- Feature Engineering ----
    df["urine"] = 0  # not available → assume normal

    X = df[
        ["age", "cholesterol", "stress", "sleep", "urine"]
    ]

    y = df["target"]

    return X, y
