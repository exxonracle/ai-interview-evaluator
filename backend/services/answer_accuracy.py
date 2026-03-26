import os
import json
from openai import AsyncOpenAI

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

async def evaluate_answer_accuracy(question: str, transcription: str):
    if not question or not question.strip():
        return None

    if api_key == "MISSING_KEY":
        return {"score": 0, "feedback": "Answer accuracy requires a GROQ_API_KEY."}

    try:
        prompt = f"""
You are an expert interview evaluator. A candidate was asked the following interview question and gave a spoken response.

Interview Question: "{question}"
Candidate's Transcribed Answer: "{transcription}"

You MUST respond with ONLY a valid JSON object in this exact format, nothing else:
{{"score": <number 1-10>, "feedback": "<2-3 sentence assessment>"}}

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
                {"role": "system", "content": "You are a professional interview evaluator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        
        result = json.loads(response.choices[0].message.content)
        return {"score": float(result.get("score", 0)), "feedback": result.get("feedback", "")}
    except Exception as e:
        return {"score": 0, "feedback": f"Answer accuracy analysis failed: {str(e)}"}
