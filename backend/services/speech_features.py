import librosa


def extract_speech_features(file_path: str, text: str):

    y, sr = librosa.load(file_path)

    duration = librosa.get_duration(y=y, sr=sr)

    word_count = len(text.split())

    # words per minute
    wpm = (word_count / duration) * 60 if duration > 0 else 0

    # better pause estimation using silence gaps
    intervals = librosa.effects.split(y, top_db=30)
    pauses = max(0, len(intervals) - 1)

    confidence = 0

    # speaking speed evaluation
    if 100 <= wpm <= 160:
        confidence += 1

    # fewer pauses indicates better fluency
    if pauses <= 5:
        confidence += 1

    clarity_score = round((confidence / 2) * 10, 2)

    return {
        "duration_seconds": round(duration, 2),
        "words_per_minute": round(wpm, 2),
        "pause_segments": pauses,
        "confidence_score": confidence,
        "clarity_score": clarity_score
    }