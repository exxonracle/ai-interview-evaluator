"""
Video & Project Demo Evaluator module.
Combines transcript analysis (clarity, confidence, structured thinking)
with visual frame analysis (UI quality, code detection, demo depth)
for a comprehensive project demonstration evaluation.
"""

import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import extract_json
from .video_frame_analyzer import extract_frames, analyze_frames_with_vision

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


async def evaluate_video_transcript(transcript: str) -> dict:
    """Analyze video transcript for communication quality indicators."""
    if not transcript or not transcript.strip():
        return {
            "clarity": 0,
            "confidence": 0,
            "structured_thinking": 0,
            "overall_video_score": 0,
            "explanation": "No video transcript provided."
        }

    if api_key == "MISSING_KEY":
        return {
            "clarity": 0,
            "confidence": 0,
            "structured_thinking": 0,
            "overall_video_score": 0,
            "explanation": "Video evaluation requires a GROQ_API_KEY."
        }

    try:
        prompt = f"""
Analyze the following project demo/video transcript and evaluate the candidate's communication abilities.

Video Transcript:
\"\"\"{transcript[:4000]}\"\"\"

Evaluate the following dimensions:
1. **Clarity**: How clearly does the candidate express ideas? Are sentences well-formed and easy to understand?
2. **Confidence**: Does the language indicate self-assurance? Look for decisive statements, lack of excessive hedging, and assertive language.
3. **Structured Thinking**: Does the candidate organize thoughts logically? Do they use frameworks, list points, or follow a coherent flow?

You MUST respond with ONLY a valid JSON object in this exact format:
{{
  "clarity": <number 1-10>,
  "confidence": <number 1-10>,
  "structured_thinking": <number 1-10>,
  "explanation": "<2-3 sentence professional assessment of the candidate's video presentation>"
}}

Score guidelines:
- 9-10: Exceptionally clear, confident, and well-structured
- 7-8: Strong communication with minor areas for improvement
- 5-6: Average, gets the point across but lacks polish
- 3-4: Below average, unclear or disorganized
- 1-2: Very poor communication, hard to follow
"""

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert communication coach and interview evaluator. Analyze transcripts objectively and provide fair scores. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content
        result = json.loads(extract_json(raw_content))

        clarity = float(result.get("clarity", 5))
        confidence = float(result.get("confidence", 5))
        structured = float(result.get("structured_thinking", 5))
        overall = round((clarity * 0.4 + confidence * 0.3 + structured * 0.3), 1)

        return {
            "clarity": clarity,
            "confidence": confidence,
            "structured_thinking": structured,
            "overall_video_score": overall,
            "explanation": result.get("explanation", "No explanation provided.")
        }

    except Exception as e:
        return {
            "clarity": 0,
            "confidence": 0,
            "structured_thinking": 0,
            "overall_video_score": 0,
            "explanation": f"Video evaluation failed: {str(e)}"
        }


async def evaluate_video_demo(video_path: str, transcript: str = "",
                               jd_requirements: dict = None) -> dict:
    """
    Full project demo evaluation combining:
    - Transcript analysis (clarity, confidence, structured thinking)
    - Visual frame analysis (UI quality, code detection, demo depth)
    Returns a combined demo evaluation with separate transcript and visual results.
    """
    result = {
        "transcript_analysis": None,
        "visual_analysis": None,
        "demo_score": 0,
        "demo_explanation": "No video provided."
    }

    # 1. Transcript analysis (if transcript exists)
    if transcript and transcript.strip():
        result["transcript_analysis"] = await evaluate_video_transcript(transcript)

    # 2. Visual frame analysis (if video file exists)
    if video_path and os.path.exists(video_path):
        frames = extract_frames(video_path, interval_seconds=3, max_frames=6)
        if frames:
            visual = await analyze_frames_with_vision(frames, transcript, jd_requirements)
            result["visual_analysis"] = visual

    # 3. Compute combined demo score
    transcript_score = 0
    visual_score = 0
    has_transcript = result["transcript_analysis"] and result["transcript_analysis"].get("overall_video_score", 0) > 0
    has_visual = result["visual_analysis"] and result["visual_analysis"].get("visual_quality", 0) > 0

    if has_transcript:
        transcript_score = result["transcript_analysis"]["overall_video_score"]
    if has_visual:
        va = result["visual_analysis"]
        visual_score = round(
            (va.get("visual_quality", 0) * 0.4 +
             va.get("demo_depth", 0) * 0.35 +
             va.get("ui_complexity", 0) * 0.25), 1
        )

    # Weight: 40% transcript, 60% visual (visual is the primary signal for demos)
    if has_transcript and has_visual:
        result["demo_score"] = round(transcript_score * 0.4 + visual_score * 0.6, 1)
    elif has_visual:
        result["demo_score"] = visual_score
    elif has_transcript:
        result["demo_score"] = transcript_score
    else:
        result["demo_score"] = 0

    # Build combined explanation
    parts = []
    if has_transcript:
        parts.append(result["transcript_analysis"].get("explanation", ""))
    if has_visual:
        parts.append(result["visual_analysis"].get("visual_explanation", ""))
    result["demo_explanation"] = " ".join(parts) if parts else "No demo data available."

    return result
