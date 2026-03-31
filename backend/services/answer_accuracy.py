import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import extract_json

# Load environment variables from .env file if it exists
load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


async def evaluate_answer_accuracy(question: str, transcription: str):
    if not question or not question.strip():
        return None

    if api_key == "MISSING_KEY":
        return {"score": 0, "feedback": "Answer accuracy requires a GROQ_API_KEY in the environment or a .env file."}

    try:
        prompt = f"""
You are an expert interview evaluator. A candidate was asked the following interview question and gave a spoken response.

Interview Question: "{question}"
Candidate's Transcribed Answer: "{transcription}"

You MUST respond with ONLY a valid JSON object in this exact format, nothing else:
{{
  "score": <number 1-10>,
  "feedback": "<2-3 sentence assessment focusing on how accurately the candidate answered the specific question>"
}}

Score guidelines:
- 9-10: Perfectly accurate and complete answer
- 7-8: Mostly accurate with minor gaps
- 5-6: Partially accurate, missing key points
- 3-4: Mostly inaccurate or off-topic
- 1-2: Completely wrong or irrelevant
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional interview evaluator. You must provide scores and feedback in JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3, # Slightly lower temperature for more predictable JSON output
            response_format={"type": "json_object"} # Groq supports JSON mode for some models
        )
        
        raw_content = response.choices[0].message.content
        try:
            result = json.loads(extract_json(raw_content))
        except json.JSONDecodeError:
            # Fallback for very messy output
            return {"score": 5.0, "feedback": f"Could not parse AI evaluation. Raw AI response: {raw_content[:150]}..."}

        return {
            "score": float(result.get("score", 0)), 
            "feedback": result.get("feedback", "No feedback provided by AI.")
        }
    except Exception as e:
        return {"score": 0, "feedback": f"Answer accuracy analysis failed: {str(e)}"}

