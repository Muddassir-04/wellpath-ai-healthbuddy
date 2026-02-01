import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_risk_model(df):
    X = df[["age", "weight", "stress", "sleep", "urine"]]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))

    with open("ml/risk_model.pkl", "wb") as f:
        pickle.dump(model, f)

    return round(acc * 100, 2)
