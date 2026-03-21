import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# sample dataset (you can expand later)
data = {
    "word_count": [5, 15, 25, 30, 8, 20],
    "sentiment": [-0.2, 0.1, 0.5, 0.7, 0.0, 0.3],
    "wpm": [80, 110, 130, 150, 90, 120],
    "pauses": [12, 8, 5, 3, 10, 6],
    "score": [3, 5, 7, 9, 4, 6]
}

df = pd.DataFrame(data)

X = df[["word_count", "sentiment", "wpm", "pauses"]]
y = df["score"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("Model trained and saved!")