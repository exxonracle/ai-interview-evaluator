from textblob import TextBlob


def analyze_text(text: str):

    blob = TextBlob(text)

    sentiment = blob.sentiment.polarity  # -1 to +1

    if sentiment > 0:
        sentiment_label = "Positive"
    elif sentiment < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    word_count = len(text.split())

    # simple scoring logic
    score = 0

    if word_count > 20:
        score += 1

    if sentiment > 0:
        score += 1

    return {
        "sentiment_score": sentiment,
        "sentiment_label": sentiment_label,
        "word_count": word_count,
        "basic_score": score
    }