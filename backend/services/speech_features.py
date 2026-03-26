import librosa
import numpy as np

def extract_speech_features(file_path: str, text: str):
    y, sr = librosa.load(file_path)
    duration = librosa.get_duration(y=y, sr=sr)
    word_count = len(text.split())
    
    # 1. Secondary Metric
    wpm = (word_count / duration) * 60 if duration > 0 else 0

    # Pause intervals (silence detection)
    intervals = librosa.effects.split(y, top_db=30)
    pauses = max(0, len(intervals) - 1)

    # 2. Flow of Words Score (out of 10)
    # Fewer pauses scaling into a score
    flow_score = max(0, 10 - (pauses * 0.5))

    # 3. Confidence Score (out of 10)
    # Using audio RMS energy as a rough proxy for vocal confidence/projection
    rms = librosa.feature.rms(y=y)
    mean_rms = np.mean(rms)
    # Scale mean RMS to a pseudo 1-10 value
    confidence_score = min(10, max(1, mean_rms * 250)) 

    # 4. Tone Score (out of 10)
    # Using pitch variation to determine dynamic, non-monotone delivery
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    pitch_variation = np.std(pitches[pitches > 0]) if len(pitches[pitches > 0]) > 0 else 0
    tone_score = min(10, max(1, pitch_variation / 60))

    # 5. Clarity Score (out of 10)
    # Base clarity on a combination of good pacing (WPM) and smooth flow
    if 110 <= wpm <= 160:
        clarity_score = flow_score
    else:
        clarity_score = max(0, flow_score - 2)

    return {
        "duration_seconds": float(round(duration, 2)),
        "words_per_minute": float(round(wpm, 2)),
        "pause_segments": int(pauses),
        "tone_score": float(round(tone_score, 2)),
        "confidence_score": float(round(confidence_score, 2)),
        "flow_score": float(round(flow_score, 2)),
        "clarity_score": float(round(clarity_score, 2))
    }