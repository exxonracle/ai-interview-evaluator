"""
Video Frame Analyzer module.
Extracts frames from video files using FFmpeg and sends them
to Groq's vision-capable LLM for visual analysis of project demos.
"""

import os
import base64
import subprocess
import tempfile
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


def extract_frames(video_path: str, interval_seconds: int = 3, max_frames: int = 6) -> list:
    """
    Extract frames from a video file at regular intervals using FFmpeg.
    Returns a list of base64-encoded JPEG images.
    """
    frames = []
    tmp_dir = tempfile.mkdtemp(prefix="frames_")

    try:
        # Use FFmpeg to extract frames at the given interval
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps=1/{interval_seconds}",
            "-frames:v", str(max_frames),
            "-q:v", "2",  # JPEG quality
            os.path.join(tmp_dir, "frame_%03d.jpg"),
            "-y", "-loglevel", "error"
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)

        # Read extracted frames as base64
        frame_files = sorted([
            f for f in os.listdir(tmp_dir) if f.endswith(".jpg")
        ])

        for fname in frame_files[:max_frames]:
            fpath = os.path.join(tmp_dir, fname)
            with open(fpath, "rb") as f:
                b64 = base64.standard_b64encode(f.read()).decode("utf-8")
                frames.append(b64)

    except subprocess.TimeoutExpired:
        print("FFmpeg frame extraction timed out")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"Frame extraction error: {e}")
    finally:
        # Cleanup temp frames
        for fname in os.listdir(tmp_dir):
            try:
                os.remove(os.path.join(tmp_dir, fname))
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass

    return frames


async def analyze_frames_with_vision(frames: list, transcript: str = "",
                                      jd_requirements: dict = None) -> dict:
    """
    Send extracted frames to a vision-capable LLM for visual analysis.
    Evaluates project demos, UI quality, code visible on screen, etc.
    """
    if not frames:
        return {
            "visual_quality": 0,
            "demo_depth": 0,
            "ui_complexity": 0,
            "code_visible": False,
            "visual_explanation": "No frames could be extracted from the video."
        }

    if api_key == "MISSING_KEY":
        return {
            "visual_quality": 0,
            "demo_depth": 0,
            "ui_complexity": 0,
            "code_visible": False,
            "visual_explanation": "Visual analysis requires a GROQ_API_KEY."
        }

    # Build JD context
    jd_context = ""
    if jd_requirements:
        jd_context = (
            f"\nJOB CONTEXT: Role={jd_requirements.get('role_title', 'Unknown')}, "
            f"Technologies={json.dumps(jd_requirements.get('key_technologies', []))}, "
            f"Domain={jd_requirements.get('domain', 'general')}"
        )

    transcript_context = ""
    if transcript:
        transcript_context = f"\nNarration transcript (what the presenter is saying): \"{transcript[:1500]}\""

    # Build message with image content
    content_parts = [
        {
            "type": "text",
            "text": f"""You are an expert technical reviewer watching a candidate's project demonstration video.
These are sequential frames (screenshots) from the demo.{jd_context}{transcript_context}

Analyze what you SEE in these frames and evaluate:
1. **Visual Quality**: Quality of the project being shown (UI design, layout, professional feel)
2. **Demo Depth**: How much of the project is being shown? Is it a shallow overview or a deep walkthrough?
3. **UI Complexity**: Complexity of what's on screen (simple page vs. complex dashboard, code editor, etc.)
4. **Code Visible**: Is any source code visible on screen? (true/false)
5. **Technologies Detected**: What technologies/tools/frameworks can you identify from the visuals?
6. **Screen Content Summary**: Brief description of what you see across the frames

You MUST respond with ONLY a valid JSON object:
{{
  "visual_quality": <number 1-10>,
  "demo_depth": <number 1-10>,
  "ui_complexity": <number 1-10>,
  "code_visible": <true/false>,
  "technologies_detected": ["<list of visible technologies, frameworks, or tools>"],
  "screen_content_summary": "<2-3 sentence description of what is shown in the demo>",
  "visual_explanation": "<2-3 sentence professional assessment of the visual demo quality>"
}}"""
        }
    ]

    # Add frame images
    for i, frame_b64 in enumerate(frames[:4]):  # Limit to 4 frames for API limits
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}"
            }
        })

    try:
        response = await client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": content_parts
                }
            ],
            max_tokens=500,
            temperature=0.3,
        )

        raw = response.choices[0].message.content

        # Try parsing JSON from the response
        try:
            result = json.loads(extract_json(raw))
        except Exception:
            # If JSON parsing fails, return a text-based result
            return {
                "visual_quality": 5,
                "demo_depth": 5,
                "ui_complexity": 5,
                "code_visible": False,
                "technologies_detected": [],
                "screen_content_summary": raw[:300],
                "visual_explanation": "Vision model response could not be parsed as JSON."
            }

        return {
            "visual_quality": float(result.get("visual_quality", 5)),
            "demo_depth": float(result.get("demo_depth", 5)),
            "ui_complexity": float(result.get("ui_complexity", 5)),
            "code_visible": bool(result.get("code_visible", False)),
            "technologies_detected": result.get("technologies_detected", []),
            "screen_content_summary": result.get("screen_content_summary", ""),
            "visual_explanation": result.get("visual_explanation", "No explanation.")
        }

    except Exception as e:
        error_msg = str(e)
        print(f"Vision analysis error: {error_msg}")
        # Graceful fallback — vision is optional
        return {
            "visual_quality": 0,
            "demo_depth": 0,
            "ui_complexity": 0,
            "code_visible": False,
            "technologies_detected": [],
            "screen_content_summary": "",
            "visual_explanation": f"Visual analysis unavailable: {error_msg[:100]}"
        }
