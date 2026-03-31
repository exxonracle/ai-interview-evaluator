import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# uses GROQ_API_KEY env var, falls back to prevent crash on import
api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


async def generate_audio_feedback(nlp_result: dict, speech_result: dict, final_evaluation: dict, transcription: str) -> str:
    if api_key == "MISSING_KEY":
        return "Standard ML-based evaluation used. (AI coaching is currently disabled. Please provide a GROQ_API_KEY environment variable to enable dynamic AI coaching feedback!)"

    try:
        prompt = f"""
Analyze the following candidate evaluation metrics and their transcription to provide a highly constructive paragraph of feedback.

Focus primarily on evaluating:
1. Tone and Confidence
2. Accent and clarity of pronunciation
3. Flow of words and natural phrasing

Note: Treat Words Per Minute (WPM) strictly as a secondary measure compared to overall flow, clarity, and confidence.

Transcription: "{transcription}"

NLP Metrics:
- Sentiment: {nlp_result.get('sentiment_label')} (Score: {nlp_result.get('sentiment_score')})

Speech & Fluency Metrics:
- Words Per Minute: {speech_result.get('words_per_minute')} (Secondary Context)
- Pause Segments: {speech_result.get('pause_segments')}
- Clarity Score: {speech_result.get('clarity_score')}

Final Evaluation:
- Out of 10: {final_evaluation.get('final_score')}
- Level: {final_evaluation.get('performance')}

Provide a professional, encouraging coaching summary (max 3-4 sentences) highlighting their strengths and advising on their confidence, flow, and clarity.
"""
        
        system_instructions = "You are a professional AI interview evaluator and communication coach. Grade candidates based heavily on tone, accent, clarity, confidence, and flow of words, keeping WPM as a secondary metric."

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Standard ML-based evaluation used. (LLM Feedback error: {str(e)})"
