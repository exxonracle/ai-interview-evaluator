import joblib

# load trained model
model = joblib.load("model.pkl")


def generate_final_score(nlp_result, speech_result):
    features = [[
        speech_result.get("tone_score", 0),
        speech_result.get("clarity_score", 0),
        speech_result.get("confidence_score", 0),
        speech_result.get("flow_score", 0)
    ]]

    predicted_score = model.predict(features)[0]

    final_score = round(min(max(predicted_score, 0), 10), 2)

    if final_score >= 8:
        level = "Excellent"
    elif final_score >= 6:
        level = "Good"
    elif final_score >= 4:
        level = "Average"
    else:
        level = "Needs Improvement"

    return {
        "final_score": final_score,
        "performance": level,
        "feedback": ["ML-based evaluation used"]
    }