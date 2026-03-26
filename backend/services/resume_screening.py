import os
import json
from PyPDF2 import PdfReader
from openai import AsyncOpenAI

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


def extract_resume_text(file_path: str) -> str:
    """Extract raw text from a PDF resume."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def extract_key_nouns(resume_text: str) -> list:
    """Pull out proper nouns, tech terms, company names from resume text for Whisper priming."""
    words = resume_text.split()
    nouns = set()
    for word in words:
        cleaned = word.strip(",.;:()[]{}\"'")
        if len(cleaned) > 2 and (cleaned[0].isupper() or any(c.isupper() for c in cleaned[1:])):
            nouns.add(cleaned)
    return list(nouns)[:50]


async def screen_resume(resume_text: str) -> dict:
    """Use LLM to analyze resume and return structured sections with scoring."""
    if api_key == "MISSING_KEY":
        return {
            "score": 0,
            "feedback": "Resume screening requires a GROQ_API_KEY.",
            "sections": None,
            "breakdown": None
        }

    try:
        prompt = f"""
Analyze the following candidate resume and extract structured information.

Resume Content:
\"\"\"{resume_text[:4000]}\"\"\"

You MUST respond with ONLY a valid JSON object in this exact format, nothing else:
{{
  "education": "<Summarize educational qualifications in 2-3 sentences. Include degrees, institutions, and years if available.>",
  "experience": "<List each work experience as a separate line. Format: 'Role at Company (Duration) - Key responsibilities'. One line per role, separated by newlines.>",
  "projects": "<List each project as a separate line. Format: 'Project Name - Technologies used - Brief description of what it does'. One line per project, separated by newlines.>",
  "skills": "<List the key technical and soft skills as a comma-separated string.>",
  "experience_score": <number 1-10 based on quality and relevance of work experience>,
  "projects_score": <number 1-10 based on complexity and impact of projects>,
  "education_score": <number 1-10 based on educational qualifications>,
  "skills_score": <number 1-10 based on breadth and depth of skills>,
  "feedback": "<2-3 sentence overall assessment of the resume>"
}}

If a section has no information, write "Not mentioned in resume." for that section.
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert HR recruiter and resume screener. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )

        result = json.loads(response.choices[0].message.content)

        # Weighted score: projects (35%) + experience (35%) + education (15%) + skills (15%)
        exp_score = float(result.get("experience_score", 5))
        proj_score = float(result.get("projects_score", 5))
        edu_score = float(result.get("education_score", 5))
        skills_score = float(result.get("skills_score", 5))
        weighted_score = round((proj_score * 0.35) + (exp_score * 0.35) + (edu_score * 0.15) + (skills_score * 0.15), 1)

        return {
            "score": weighted_score,
            "feedback": result.get("feedback", ""),
            "sections": {
                "education": result.get("education", "Not mentioned in resume."),
                "experience": result.get("experience", "Not mentioned in resume."),
                "projects": result.get("projects", "Not mentioned in resume."),
                "skills": result.get("skills", "Not mentioned in resume.")
            },
            "breakdown": {
                "experience_score": exp_score,
                "projects_score": proj_score,
                "education_score": edu_score,
                "skills_score": skills_score
            }
        }
    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Resume screening failed: {str(e)}",
            "sections": None,
            "breakdown": None
        }
