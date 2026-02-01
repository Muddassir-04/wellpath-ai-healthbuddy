import pandas as pd

def compute_health_change(df):
    if df is None or len(df) < 6:
        return None

    recent = df.tail(6)

    first_half = recent.iloc[:3]["risk_score"].mean()
    second_half = recent.iloc[3:]["risk_score"].mean()

    change = second_half - first_half

    return round(change, 2)
