"""
Database module for the Skill-Based Hiring Platform.
Uses SQLite via aiosqlite for async operations.
Stores candidate profiles and their evaluation reports.
"""

import os
import json
import aiosqlite
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "hiring_platform.db")


async def init_db():
    """Initialize database tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                resume_score REAL,
                interview_score REAL,
                github_score REAL,
                video_score REAL,
                technical_skill REAL,
                communication REAL,
                problem_solving REAL,
                overall_score REAL,
                full_report TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
            )
        """)
        await db.commit()


async def save_candidate(name: str, email: str = None) -> int:
    """Save a new candidate and return their ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO candidates (name, email, created_at) VALUES (?, ?, ?)",
            (name, email, datetime.utcnow().isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def save_evaluation(candidate_id: int, scores: dict, full_report: dict) -> int:
    """Save evaluation results for a candidate."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO evaluations 
               (candidate_id, resume_score, interview_score, github_score, video_score,
                technical_skill, communication, problem_solving, overall_score,
                full_report, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                candidate_id,
                scores.get("resume_score"),
                scores.get("interview_score"),
                scores.get("github_score"),
                scores.get("video_score"),
                scores.get("technical_skill"),
                scores.get("communication"),
                scores.get("problem_solving"),
                scores.get("overall_score"),
                json.dumps(full_report),
                datetime.utcnow().isoformat()
            )
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_evaluations() -> list:
    """Get all candidates with their latest evaluation scores."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.id, c.name, c.email, c.created_at,
                   e.resume_score, e.interview_score, e.github_score, e.video_score,
                   e.technical_skill, e.communication, e.problem_solving, e.overall_score,
                   e.id as evaluation_id
            FROM candidates c
            LEFT JOIN evaluations e ON c.id = e.candidate_id
            ORDER BY c.created_at DESC
        """)
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "created_at": row["created_at"],
                "evaluation_id": row["evaluation_id"],
                "resume_score": row["resume_score"],
                "interview_score": row["interview_score"],
                "github_score": row["github_score"],
                "video_score": row["video_score"],
                "technical_skill": row["technical_skill"],
                "communication": row["communication"],
                "problem_solving": row["problem_solving"],
                "overall_score": row["overall_score"]
            })
        return results


async def get_evaluation(candidate_id: int) -> dict:
    """Get detailed evaluation for a specific candidate."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.id, c.name, c.email, c.created_at as candidate_created_at,
                   e.resume_score, e.interview_score, e.github_score, e.video_score,
                   e.technical_skill, e.communication, e.problem_solving, e.overall_score,
                   e.full_report, e.created_at as evaluation_date
            FROM candidates c
            LEFT JOIN evaluations e ON c.id = e.candidate_id
            WHERE c.id = ?
        """, (candidate_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        
        full_report = None
        if row["full_report"]:
            try:
                full_report = json.loads(row["full_report"])
            except json.JSONDecodeError:
                full_report = None

        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "created_at": row["candidate_created_at"],
            "evaluation_date": row["evaluation_date"],
            "resume_score": row["resume_score"],
            "interview_score": row["interview_score"],
            "github_score": row["github_score"],
            "video_score": row["video_score"],
            "technical_skill": row["technical_skill"],
            "communication": row["communication"],
            "problem_solving": row["problem_solving"],
            "overall_score": row["overall_score"],
            "full_report": full_report
        }


async def get_rankings() -> list:
    """Get candidates ranked by overall score (descending)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.id, c.name, c.email,
                   e.technical_skill, e.communication, e.problem_solving, e.overall_score,
                   e.resume_score, e.interview_score, e.github_score, e.video_score
            FROM candidates c
            INNER JOIN evaluations e ON c.id = e.candidate_id
            WHERE e.overall_score IS NOT NULL
            ORDER BY e.overall_score DESC
        """)
        rows = await cursor.fetchall()
        results = []
        for rank, row in enumerate(rows, 1):
            results.append({
                "rank": rank,
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "technical_skill": row["technical_skill"],
                "communication": row["communication"],
                "problem_solving": row["problem_solving"],
                "overall_score": row["overall_score"],
                "resume_score": row["resume_score"],
                "interview_score": row["interview_score"],
                "github_score": row["github_score"],
                "video_score": row["video_score"]
            })
        return results


async def delete_candidate(candidate_id: int) -> bool:
    """Delete a candidate and their evaluations."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if candidate exists
        cursor = await db.execute("SELECT id FROM candidates WHERE id = ?", (candidate_id,))
        if not await cursor.fetchone():
            return False
        await db.execute("DELETE FROM evaluations WHERE candidate_id = ?", (candidate_id,))
        await db.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        await db.commit()
        return True
