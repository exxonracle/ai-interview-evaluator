"""
Scoring Engine module.
Combines scores from all four evaluation modules using a weighted formula
and produces composite scores for technical skill, communication, and problem-solving.
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

# Module weights
WEIGHTS = {
    "resume": 0.30,
    "interview": 0.30,
    "github": 0.20,
    "video": 0.20
}


def calculate_combined_score(resume_result: dict, interview_result: dict,
                              github_result: dict, video_result: dict) -> dict:
    """
    Combine all module scores using the weighted formula.
    Resume (30%), Interview (30%), GitHub (20%), Video (20%)
    
    Outputs composite scores: technical_skill, communication, problem_solving, overall_score
    """
    # Extract overall scores from each module
    resume_score = resume_result.get("overall_resume_score", 0) or 0
    interview_score = interview_result.get("overall_interview_score", 0) or 0
    github_score = github_result.get("overall_github_score", 0) or 0
    video_score = video_result.get("overall_video_score", 0) or 0

    # Weighted overall score
    overall_score = round(
        resume_score * WEIGHTS["resume"] +
        interview_score * WEIGHTS["interview"] +
        github_score * WEIGHTS["github"] +
        video_score * WEIGHTS["video"],
        1
    )

    # Composite: Technical Skill
    # Derived from: resume skills + interview correctness + github code quality
    tech_resume = resume_result.get("skills_score", 0) or 0
    tech_interview = interview_result.get("correctness", 0) or 0
    tech_github = github_result.get("code_quality", 0) or 0
    technical_skill = round((tech_resume * 0.30 + tech_interview * 0.35 + tech_github * 0.35), 1)

    # Composite: Communication
    # Derived from: interview communication + video clarity + video confidence
    comm_interview = interview_result.get("communication", 0) or 0
    comm_video_clarity = video_result.get("clarity", 0) or 0
    comm_video_confidence = video_result.get("confidence", 0) or 0
    communication = round((comm_interview * 0.40 + comm_video_clarity * 0.35 + comm_video_confidence * 0.25), 1)

    # Composite: Problem Solving
    # Derived from: interview problem_solving + github complexity + video structured_thinking
    ps_interview = interview_result.get("problem_solving", 0) or 0
    ps_github = github_result.get("complexity", 0) or 0
    ps_video = video_result.get("structured_thinking", 0) or 0
    problem_solving = round((ps_interview * 0.45 + ps_github * 0.30 + ps_video * 0.25), 1)

    return {
        "resume_score": resume_score,
        "interview_score": interview_score,
        "github_score": github_score,
        "video_score": video_score,
        "technical_skill": technical_skill,
        "communication": communication,
        "problem_solving": problem_solving,
        "overall_score": overall_score
    }


async def generate_score_explanations(scores: dict, resume_result: dict,
                                       interview_result: dict, github_result: dict,
                                       video_result: dict) -> dict:
    """Generate LLM explanations for each composite score."""
    if api_key == "MISSING_KEY":
        return {
            "technical_skill_explanation": "LLM explanations disabled (no API key).",
            "communication_explanation": "LLM explanations disabled (no API key).",
            "problem_solving_explanation": "LLM explanations disabled (no API key).",
            "overall_explanation": "LLM explanations disabled (no API key)."
        }

    try:
        prompt = f"""
A candidate has been evaluated across 4 dimensions. Based on the scores and individual module feedback, provide concise explanations for each composite score.

Module Scores:
- Resume: {scores['resume_score']}/10 — {resume_result.get('explanation', 'N/A')}
- Interview: {scores['interview_score']}/10 — {interview_result.get('explanation', 'N/A')}
- GitHub: {scores['github_score']}/10 — {github_result.get('explanation', 'N/A')}
- Video: {scores['video_score']}/10 — {video_result.get('explanation', 'N/A')}

Composite Scores:
- Technical Skill: {scores['technical_skill']}/10
- Communication: {scores['communication']}/10
- Problem Solving: {scores['problem_solving']}/10
- Overall: {scores['overall_score']}/10

You MUST respond with ONLY a valid JSON object:
{{
  "technical_skill_explanation": "<1-2 sentence explanation of the technical skill score>",
  "communication_explanation": "<1-2 sentence explanation of the communication score>",
  "problem_solving_explanation": "<1-2 sentence explanation of the problem-solving score>",
  "overall_explanation": "<2-3 sentence summary of the candidate's overall profile>"
}}
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a hiring expert. Provide concise, professional explanations for candidate evaluation scores. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content
        result = json.loads(extract_json(raw_content))

        return {
            "technical_skill_explanation": result.get("technical_skill_explanation", ""),
            "communication_explanation": result.get("communication_explanation", ""),
            "problem_solving_explanation": result.get("problem_solving_explanation", ""),
            "overall_explanation": result.get("overall_explanation", "")
        }

    except Exception as e:
        return {
            "technical_skill_explanation": f"Explanation generation failed: {str(e)}",
            "communication_explanation": "",
            "problem_solving_explanation": "",
            "overall_explanation": ""
        }
