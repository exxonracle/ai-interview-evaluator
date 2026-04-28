"""
Interview Transcript Evaluator module.
Evaluates interview transcripts for communication skills, 
correctness, and problem-solving approach using Groq LLM.
"""

import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import extract_json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


async def evaluate_interview(transcript: str) -> dict:
    """Evaluate interview transcript for communication, correctness, and problem-solving."""
    if not transcript or not transcript.strip():
        return {
            "communication": 0,
            "correctness": 0,
            "problem_solving": 0,
            "overall_interview_score": 0,
            "explanation": "No interview transcript provided."
        }

    if api_key == "MISSING_KEY":
        return {
            "communication": 0,
            "correctness": 0,
            "problem_solving": 0,
            "overall_interview_score": 0,
            "explanation": "Interview evaluation requires a GROQ_API_KEY."
        }

    try:
        prompt = f"""
Analyze the following interview transcript and evaluate the candidate's performance.

Interview Transcript:
\"\"\"{transcript[:4000]}\"\"\"

Evaluate the following dimensions:
1. **Communication**: How well does the candidate articulate ideas? Is the language professional, clear, and appropriate for an interview?
2. **Correctness**: Are the candidate's technical answers, examples, and claims accurate? Do they demonstrate genuine knowledge?
3. **Problem Solving**: Does the candidate show analytical thinking? Do they break down problems, consider edge cases, and propose structured solutions?

You MUST respond with ONLY a valid JSON object in this exact format:
{{
  "communication": <number 1-10>,
  "correctness": <number 1-10>,
  "problem_solving": <number 1-10>,
  "explanation": "<2-3 sentence professional assessment of the candidate's interview performance>"
}}

Score guidelines:
- 9-10: Outstanding, demonstrates mastery and excellent articulation
- 7-8: Strong performance with minor gaps
- 5-6: Average, meets basic expectations
- 3-4: Below average, significant gaps in knowledge or communication
- 1-2: Poor, unable to demonstrate competency
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a senior technical interviewer. Evaluate candidates objectively based on their transcript. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content
        result = json.loads(extract_json(raw_content))

        communication = float(result.get("communication", 5))
        correctness = float(result.get("correctness", 5))
        problem_solving = float(result.get("problem_solving", 5))
        overall = round((communication * 0.35 + correctness * 0.35 + problem_solving * 0.30), 1)

        return {
            "communication": communication,
            "correctness": correctness,
            "problem_solving": problem_solving,
            "overall_interview_score": overall,
            "explanation": result.get("explanation", "No explanation provided.")
        }

    except Exception as e:
        return {
            "communication": 0,
            "correctness": 0,
            "problem_solving": 0,
            "overall_interview_score": 0,
            "explanation": f"Interview evaluation failed: {str(e)}"
        }
