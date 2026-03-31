import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib


data = {
    "tone_score": [5.0, 7.5, 8.0, 9.0, 4.0, 6.0],
    "clarity_score": [2.0, 5.0, 8.0, 10.0, 3.0, 7.0],
    "confidence_score": [4.0, 6.0, 8.5, 9.5, 3.5, 5.5],
    "flow_score": [3.0, 5.5, 7.5, 9.0, 2.5, 6.5],
    "wpm": [80, 110, 130, 150, 90, 120],
    "score": [3, 5, 8, 9, 3, 6]
}

df = pd.DataFrame(data)


X = df[["tone_score", "clarity_score", "confidence_score", "flow_score"]]
y = df["score"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("Model trained and saved!")