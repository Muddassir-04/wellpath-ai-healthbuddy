import pandas as pd

def build_dataset(logs):
    df = pd.DataFrame(logs)

    # Drop unnecessary fields
    df = df.drop(columns=["timestamp", "recommended_action", "id"], errors="ignore")

    # Encode urine frequency
    df["urine"] = df["urine"].map({"normal": 0, "increased": 1})

    # Encode risk label (target)
    df["target"] = df["risk_level"].map({
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 1
    })

    # Drop rows with missing values
    df = df.dropna()

    return df
