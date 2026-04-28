"""
Resume Analyzer module for the Hiring Platform.
Dedicated resume analysis that evaluates skills depth, 
experience relevance, and provides scoring for the hiring pipeline.
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


async def analyze_resume_text(resume_text: str) -> dict:
    """Analyze resume text for skills, experience, and provide scoring."""
    if not resume_text or not resume_text.strip():
        return {
            "skills_score": 0,
            "experience_score": 0,
            "education_score": 0,
            "projects_score": 0,
            "overall_resume_score": 0,
            "explanation": "No resume text provided."
        }

    if api_key == "MISSING_KEY":
        return {
            "skills_score": 0,
            "experience_score": 0,
            "education_score": 0,
            "projects_score": 0,
            "overall_resume_score": 0,
            "explanation": "Resume analysis requires a GROQ_API_KEY."
        }

    try:
        prompt = f"""
Analyze the following resume text and evaluate the candidate's qualifications for a technical role.

Resume:
\"\"\"{resume_text[:4000]}\"\"\"

Evaluate the following dimensions:
1. **Skills**: Depth and breadth of technical and soft skills listed. Modern, in-demand skills score higher.
2. **Experience**: Quality, relevance, and duration of work experience. Leadership and impact score higher.
3. **Education**: Quality of educational background, relevant certifications, and continuous learning.
4. **Projects**: Complexity, impact, and technical depth of personal or professional projects.

You MUST respond with ONLY a valid JSON object in this exact format:
{{
  "skills_score": <number 1-10>,
  "experience_score": <number 1-10>,
  "education_score": <number 1-10>,
  "projects_score": <number 1-10>,
  "explanation": "<2-3 sentence professional assessment of the candidate's resume>"
}}

Score guidelines:
- 9-10: Exceptional qualifications, top-tier candidate
- 7-8: Strong profile with relevant experience
- 5-6: Average, meets basic requirements
- 3-4: Below average, limited relevant experience
- 1-2: Minimal qualifications
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter. Evaluate resumes objectively, focusing on technical abilities and career trajectory. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content
        result = json.loads(extract_json(raw_content))

        skills = float(result.get("skills_score", 5))
        experience = float(result.get("experience_score", 5))
        education = float(result.get("education_score", 5))
        projects = float(result.get("projects_score", 5))
        # Weighted: experience (35%) + projects (30%) + skills (20%) + education (15%)
        overall = round((experience * 0.35 + projects * 0.30 + skills * 0.20 + education * 0.15), 1)

        return {
            "skills_score": skills,
            "experience_score": experience,
            "education_score": education,
            "projects_score": projects,
            "overall_resume_score": overall,
            "explanation": result.get("explanation", "No explanation provided.")
        }

    except Exception as e:
        return {
            "skills_score": 0,
            "experience_score": 0,
            "education_score": 0,
            "projects_score": 0,
            "overall_resume_score": 0,
            "explanation": f"Resume analysis failed: {str(e)}"
        }
