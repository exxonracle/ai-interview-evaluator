from services.utils import extract_json
from services.resume_screening import client

async def refine_transcript(raw_transcript: str, resume_text: str, candidate_name: str):
    """
    Uses LLM to cross-reference the transcript with resume data 
    to fix misspellings of names, institutes, and technical nouns.
    """
    if not raw_transcript or not resume_text:
        return raw_transcript

    prompt = f"""
    You are an expert transcription editor. I have a transcript of an interview and a candidate's resume.
    The transcription (Whisper) might have misspelled proper nouns (names, companies, technologies, universities).

    CANDIDATE NAME: {candidate_name}
    
    CANDIDATE RESUME DATA:
    {resume_text[:2000]}

    RAW TRANSCRIPT:
    "{raw_transcript}"

    TASK:
    1. Identify names, institutes, and technical terms in the transcript that look like they might be phonetic misspellings of terms found in the resume.
    2. Correct them using the resume as the "ground truth".
    3. Output ONLY the corrected transcript. Maintain the original speaking style and flow. Do not add commentary.

    CORRECTED TRANSCRIPT:
    """

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        refined_text = response.choices[0].message.content.strip()
        # Remove quotes if the LLM added them
        if refined_text.startswith('"') and refined_text.endswith('"'):
            refined_text = refined_text[1:-1]
        return refined_text
    except Exception as e:
        print(f"Error refining transcript: {e}")
        return raw_transcript
