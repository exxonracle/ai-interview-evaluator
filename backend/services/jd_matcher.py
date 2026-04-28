"""
JD Matcher module.
Takes all module results + JD requirements and computes a role-fit score
with detailed explanations of how well the candidate matches.
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


async def compute_jd_match(jd_requirements: dict, resume_result: dict,
                           interview_result: dict, github_result: dict,
                           video_result: dict, scores: dict) -> dict:
    """
    Compute how well a candidate matches a specific Job Description.
    Cross-references all module results against JD requirements.
    """
    if not jd_requirements:
        return None

    if api_key == "MISSING_KEY":
        return None

    try:
        prompt = f"""
You are an expert technical recruiter. Evaluate how well this candidate matches the job requirements.

JOB REQUIREMENTS:
- Role: {jd_requirements.get('role_title', 'Unknown')}
- Experience Level: {jd_requirements.get('experience_level', 'Unknown')}
- Min Years: {jd_requirements.get('min_years_experience', 0)}
- Required Skills: {json.dumps(jd_requirements.get('required_skills', []))}
- Preferred Skills: {json.dumps(jd_requirements.get('preferred_skills', []))}
- Key Technologies: {json.dumps(jd_requirements.get('key_technologies', []))}
- Domain: {jd_requirements.get('domain', 'general')}
- Responsibilities: {json.dumps(jd_requirements.get('responsibilities', []))}
- Soft Skills: {json.dumps(jd_requirements.get('soft_skills', []))}

CANDIDATE EVALUATION:
- Resume Analysis: {json.dumps(resume_result)}
- Interview Analysis: {json.dumps(interview_result)}
- GitHub Analysis: {json.dumps(github_result)}
- Video Analysis: {json.dumps(video_result)}
- Composite Scores: Technical={scores.get('technical_skill', 0)}, Communication={scores.get('communication', 0)}, Problem Solving={scores.get('problem_solving', 0)}, Overall={scores.get('overall_score', 0)}

You MUST respond with ONLY a valid JSON object in this exact format:
{{
  "overall_fit_score": <number 1-10, how well candidate fits this specific role>,
  "skills_match_score": <number 1-10, how many required/preferred skills the candidate has>,
  "experience_match_score": <number 1-10, does their experience level match>,
  "domain_relevance_score": <number 1-10, how relevant is their background to this domain>,
  "matched_skills": ["<skills from JD that candidate demonstrably has>"],
  "missing_skills": ["<required skills from JD that candidate appears to lack>"],
  "strengths_for_role": ["<top 3 reasons candidate is a good fit>"],
  "concerns_for_role": ["<top 2-3 concerns or gaps for this role>"],
  "recommendation": "<STRONG FIT / GOOD FIT / MODERATE FIT / WEAK FIT / NOT RECOMMENDED>",
  "explanation": "<2-3 sentence professional assessment of candidate-to-role fit>"
}}

Score guidelines:
- 9-10: Exceptional match, candidate exceeds requirements
- 7-8: Strong match, meets most requirements
- 5-6: Moderate match, some gaps but trainable
- 3-4: Weak match, significant skill gaps
- 1-2: Poor match, fundamentally different background
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert recruiter evaluating candidate-to-role fit. Be fair, objective, and detailed. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        result = json.loads(extract_json(raw))

        return {
            "overall_fit_score": float(result.get("overall_fit_score", 0)),
            "skills_match_score": float(result.get("skills_match_score", 0)),
            "experience_match_score": float(result.get("experience_match_score", 0)),
            "domain_relevance_score": float(result.get("domain_relevance_score", 0)),
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "strengths_for_role": result.get("strengths_for_role", []),
            "concerns_for_role": result.get("concerns_for_role", []),
            "recommendation": result.get("recommendation", "UNKNOWN"),
            "explanation": result.get("explanation", "No explanation available."),
        }

    except Exception as e:
        print(f"JD match error: {e}")
        return {
            "overall_fit_score": 0,
            "explanation": f"JD matching failed: {str(e)}",
            "recommendation": "ERROR",
        }
