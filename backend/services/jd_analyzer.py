"""
Job Description (JD) Analyzer module.
Extracts key requirements, skills, experience level, and role type from a JD
so other modules can use this context for JD-aware scoring.
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


async def analyze_jd(jd_text: str) -> dict:
    """
    Extract structured requirements from a Job Description.
    Returns a dict with role info, required skills, experience level, etc.
    """
    if not jd_text or not jd_text.strip():
        return None

    if api_key == "MISSING_KEY":
        return None

    try:
        prompt = f"""
Analyze the following Job Description and extract structured requirements.

JOB DESCRIPTION:
{jd_text[:3000]}

You MUST respond with ONLY a valid JSON object in this exact format:
{{
  "role_title": "<extracted job title, e.g. 'Senior Backend Engineer'>",
  "department": "<department or team, e.g. 'Platform Engineering'>",
  "experience_level": "<junior/mid/senior/lead/principal>",
  "min_years_experience": <number or 0 if not specified>,
  "required_skills": ["<list of must-have technical skills>"],
  "preferred_skills": ["<list of nice-to-have skills>"],
  "key_technologies": ["<specific tools, frameworks, languages mentioned>"],
  "domain": "<industry domain, e.g. 'fintech', 'healthcare', 'e-commerce', 'general'>",
  "responsibilities": ["<top 3-5 key responsibilities>"],
  "soft_skills": ["<communication, leadership, teamwork, etc.>"],
  "education_preference": "<preferred education, e.g. 'BS in CS' or 'any'>",
  "summary": "<1-2 sentence summary of what this role needs>"
}}
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst. Extract structured requirements from job descriptions. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        result = json.loads(extract_json(raw))
        return result

    except Exception as e:
        print(f"JD analysis error: {e}")
        return None
