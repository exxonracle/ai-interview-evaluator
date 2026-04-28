"""
GitHub Repository & Portfolio Analyzer module.
Supports both single repo URLs and full account/profile URLs.
When a JD is provided, it selects and evaluates the most relevant repos
based on the job requirements.
"""

import os
import re
import json
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .utils import extract_json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "MISSING_KEY")
github_token = os.getenv("GITHUB_TOKEN", None)

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


def parse_github_input(url: str) -> dict:
    """
    Detect whether the URL is a single repo or an account/profile.
    Returns {"type": "repo", "owner": ..., "repo": ...}
    or     {"type": "account", "username": ...}
    """
    url = url.strip().rstrip("/")

    # Match repo: github.com/owner/repo
    repo_patterns = [
        r"github\.com/([^/]+)/([^/\s?#]+)",
        r"^([^/]+)/([^/\s]+)$"
    ]
    for pattern in repo_patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2).replace(".git", "")
            # Check if this is just a username (no repo part that's a real repo name)
            # If owner matches common GitHub paths, skip
            if repo in ("", "tab=repositories", "repositories"):
                return {"type": "account", "username": owner}
            return {"type": "repo", "owner": owner, "repo": repo}

    # Match account: github.com/username or just username
    account_patterns = [
        r"github\.com/([^/\s?#]+)$",
        r"^([a-zA-Z0-9_-]+)$"
    ]
    for pattern in account_patterns:
        match = re.search(pattern, url)
        if match:
            username = match.group(1)
            return {"type": "account", "username": username}

    return {"type": "unknown"}


def _get_headers():
    """Build GitHub API headers."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    return headers


async def fetch_repo_data(owner: str, repo: str) -> dict:
    """Fetch single repository metadata from GitHub API."""
    headers = _get_headers()

    async with httpx.AsyncClient(timeout=15.0) as http_client:
        try:
            # Fetch repo info
            repo_resp = await http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers
            )
            if repo_resp.status_code != 200:
                return {"error": f"GitHub API returned {repo_resp.status_code}"}
            repo_data = repo_resp.json()

            # Fetch languages
            lang_resp = await http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/languages",
                headers=headers
            )
            languages = lang_resp.json() if lang_resp.status_code == 200 else {}

            # Fetch recent commits (last 10)
            commits_resp = await http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=10",
                headers=headers
            )
            commits = []
            if commits_resp.status_code == 200:
                for c in commits_resp.json()[:10]:
                    commits.append(c.get("commit", {}).get("message", "")[:100])

            # Fetch top-level file tree
            tree_resp = await http_client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/",
                headers=headers
            )
            file_tree = []
            if tree_resp.status_code == 200:
                for item in tree_resp.json()[:30]:
                    file_tree.append({
                        "name": item.get("name"),
                        "type": item.get("type"),
                        "size": item.get("size", 0)
                    })

            return {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description", ""),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "size_kb": repo_data.get("size", 0),
                "default_branch": repo_data.get("default_branch", "main"),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "languages": languages,
                "recent_commits": commits,
                "file_tree": file_tree,
                "topics": repo_data.get("topics", [])
            }

        except httpx.TimeoutException:
            return {"error": "GitHub API request timed out"}
        except Exception as e:
            return {"error": f"Failed to fetch GitHub data: {str(e)}"}


async def fetch_account_repos(username: str) -> dict:
    """
    Fetch all public repos for a GitHub account.
    Returns account-level summary + list of repos sorted by relevance.
    """
    headers = _get_headers()

    async with httpx.AsyncClient(timeout=20.0) as http_client:
        try:
            # Fetch user profile
            user_resp = await http_client.get(
                f"https://api.github.com/users/{username}",
                headers=headers
            )
            if user_resp.status_code != 200:
                return {"error": f"User not found: {username}"}
            user_data = user_resp.json()

            # Fetch repos (up to 100, sorted by stars/updated)
            repos_resp = await http_client.get(
                f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated&type=owner",
                headers=headers
            )
            if repos_resp.status_code != 200:
                return {"error": "Could not fetch repositories"}

            repos_raw = repos_resp.json()

            # Build repo summaries
            repos = []
            total_stars = 0
            all_languages = {}

            for r in repos_raw:
                if r.get("fork"):
                    continue  # Skip forks

                stars = r.get("stargazers_count", 0)
                total_stars += stars
                lang = r.get("language")
                if lang:
                    all_languages[lang] = all_languages.get(lang, 0) + 1

                repos.append({
                    "name": r.get("name"),
                    "full_name": r.get("full_name"),
                    "description": r.get("description", ""),
                    "stars": stars,
                    "forks": r.get("forks_count", 0),
                    "language": lang,
                    "size_kb": r.get("size", 0),
                    "topics": r.get("topics", []),
                    "updated_at": r.get("updated_at"),
                    "created_at": r.get("created_at"),
                })

            return {
                "username": username,
                "name": user_data.get("name", username),
                "bio": user_data.get("bio", ""),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "total_stars": total_stars,
                "all_languages": all_languages,
                "repos": repos,  # Non-fork repos sorted by recent update
            }

        except httpx.TimeoutException:
            return {"error": "GitHub API request timed out"}
        except Exception as e:
            return {"error": f"Failed to fetch account data: {str(e)}"}


async def _select_top_repos(repos: list, jd_requirements: dict = None, max_repos: int = 3) -> list:
    """
    Use LLM to pick the most relevant repos based on JD context.
    If no JD, pick by stars + recency.
    """
    if not repos:
        return []

    if not jd_requirements or api_key == "MISSING_KEY":
        # Fallback: sort by stars, pick top N
        sorted_repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)
        return sorted_repos[:max_repos]

    try:
        repo_summaries = []
        for i, r in enumerate(repos[:30]):  # Limit to 30 for prompt size
            repo_summaries.append(
                f"{i}. {r['name']} — {r.get('description', 'N/A')} | "
                f"Lang: {r.get('language', '?')} | Stars: {r.get('stars', 0)} | "
                f"Topics: {', '.join(r.get('topics', []))}"
            )

        prompt = f"""
Given this Job Description context and a list of GitHub repositories, 
select the {max_repos} MOST RELEVANT repositories that best demonstrate 
skills needed for this role.

JOB CONTEXT:
- Role: {jd_requirements.get('role_title', 'Unknown')}
- Key Technologies: {json.dumps(jd_requirements.get('key_technologies', []))}
- Required Skills: {json.dumps(jd_requirements.get('required_skills', []))}
- Domain: {jd_requirements.get('domain', 'general')}

REPOSITORIES:
{chr(10).join(repo_summaries)}

Respond with ONLY a JSON object:
{{
  "selected_indices": [<indices of the {max_repos} most relevant repos>],
  "reasoning": "<1 sentence explaining why these repos are most relevant>"
}}
"""
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert recruiter selecting the most role-relevant GitHub projects. Respond with JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        result = json.loads(extract_json(raw))
        indices = result.get("selected_indices", [0, 1, 2])

        selected = []
        for idx in indices:
            if 0 <= idx < len(repos):
                selected.append(repos[idx])
        return selected if selected else repos[:max_repos]

    except Exception:
        # Fallback
        sorted_repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)
        return sorted_repos[:max_repos]


async def _evaluate_repo_with_llm(repo_data: dict, jd_requirements: dict = None) -> dict:
    """Evaluate a single repo using LLM, optionally with JD context."""
    jd_context = ""
    if jd_requirements:
        jd_context = f"""
JOB CONTEXT (evaluate relevance to this role):
- Role: {jd_requirements.get('role_title', 'Unknown')}
- Key Technologies: {json.dumps(jd_requirements.get('key_technologies', []))}
- Domain: {jd_requirements.get('domain', 'general')}
"""

    prompt = f"""
Analyze this GitHub repository and evaluate the developer's capabilities.
{jd_context}

Repository: {repo_data.get('full_name', 'Unknown')}
Description: {repo_data.get('description', 'No description')}
Stars: {repo_data.get('stars', 0)} | Forks: {repo_data.get('forks', 0)}
Size: {repo_data.get('size_kb', 0)} KB
Languages: {json.dumps(repo_data.get('languages', {}))}
Topics: {', '.join(repo_data.get('topics', []))}
File Structure: {json.dumps(repo_data.get('file_tree', [])[:20])}
Recent Commits: {json.dumps(repo_data.get('recent_commits', [])[:5])}

You MUST respond with ONLY a valid JSON object:
{{
  "code_quality": <number 1-10>,
  "tech_stack_breadth": <number 1-10>,
  "complexity": <number 1-10>,
  "jd_relevance": <number 1-10, how relevant is this project to the job requirements. If no JD context, score 5>,
  "explanation": "<2-3 sentence assessment>"
}}
"""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert software engineering evaluator. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    return json.loads(extract_json(raw))


async def analyze_github_repo(github_input: str, jd_requirements: dict = None) -> dict:
    """
    Analyze a GitHub repo or account.
    - If input is a repo URL → single repo analysis
    - If input is a profile/username → portfolio analysis (picks top repos, JD-aware)
    """
    if not github_input or not github_input.strip():
        return {
            "code_quality": 0,
            "tech_stack_breadth": 0,
            "complexity": 0,
            "jd_relevance": 0,
            "overall_github_score": 0,
            "explanation": "No GitHub repository URL provided.",
            "mode": "none"
        }

    parsed = parse_github_input(github_input)

    if parsed["type"] == "unknown":
        return {
            "code_quality": 0,
            "tech_stack_breadth": 0,
            "complexity": 0,
            "jd_relevance": 0,
            "overall_github_score": 0,
            "explanation": f"Could not parse GitHub input: {github_input}",
            "mode": "error"
        }

    if api_key == "MISSING_KEY":
        return {
            "code_quality": 0,
            "tech_stack_breadth": 0,
            "complexity": 0,
            "jd_relevance": 0,
            "overall_github_score": 0,
            "explanation": "GitHub analysis requires a GROQ_API_KEY.",
            "mode": "error"
        }

    try:
        # =============================================
        # SINGLE REPO MODE
        # =============================================
        if parsed["type"] == "repo":
            repo_data = await fetch_repo_data(parsed["owner"], parsed["repo"])
            if "error" in repo_data:
                return {
                    "code_quality": 0, "tech_stack_breadth": 0, "complexity": 0,
                    "jd_relevance": 0, "overall_github_score": 0,
                    "explanation": f"Could not analyze repo: {repo_data['error']}",
                    "mode": "repo"
                }

            result = await _evaluate_repo_with_llm(repo_data, jd_requirements)

            code_quality = float(result.get("code_quality", 5))
            tech_stack = float(result.get("tech_stack_breadth", 5))
            complexity = float(result.get("complexity", 5))
            jd_relevance = float(result.get("jd_relevance", 5))
            overall = round((code_quality * 0.3 + tech_stack * 0.2 + complexity * 0.2 + jd_relevance * 0.3), 1)

            return {
                "code_quality": code_quality,
                "tech_stack_breadth": tech_stack,
                "complexity": complexity,
                "jd_relevance": jd_relevance,
                "overall_github_score": overall,
                "explanation": result.get("explanation", ""),
                "mode": "repo",
                "repo_info": {
                    "name": repo_data.get("full_name"),
                    "stars": repo_data.get("stars"),
                    "languages": repo_data.get("languages"),
                    "description": repo_data.get("description")
                }
            }

        # =============================================
        # PORTFOLIO MODE (full account)
        # =============================================
        elif parsed["type"] == "account":
            account_data = await fetch_account_repos(parsed["username"])
            if "error" in account_data:
                return {
                    "code_quality": 0, "tech_stack_breadth": 0, "complexity": 0,
                    "jd_relevance": 0, "overall_github_score": 0,
                    "explanation": f"Could not analyze account: {account_data['error']}",
                    "mode": "portfolio"
                }

            repos = account_data.get("repos", [])
            if not repos:
                return {
                    "code_quality": 0, "tech_stack_breadth": 0, "complexity": 0,
                    "jd_relevance": 0, "overall_github_score": 0,
                    "explanation": f"No public repositories found for {parsed['username']}.",
                    "mode": "portfolio"
                }

            # Select most relevant repos (JD-aware)
            top_repos = await _select_top_repos(repos, jd_requirements, max_repos=3)

            # Fetch detailed data + evaluate each selected repo
            repo_evaluations = []
            for repo_summary in top_repos:
                full_name = repo_summary.get("full_name", "")
                parts = full_name.split("/")
                if len(parts) == 2:
                    detailed_data = await fetch_repo_data(parts[0], parts[1])
                    if "error" not in detailed_data:
                        eval_result = await _evaluate_repo_with_llm(detailed_data, jd_requirements)
                        eval_result["repo_name"] = full_name
                        eval_result["stars"] = detailed_data.get("stars", 0)
                        eval_result["description"] = detailed_data.get("description", "")
                        eval_result["languages"] = detailed_data.get("languages", {})
                        repo_evaluations.append(eval_result)

            if not repo_evaluations:
                return {
                    "code_quality": 0, "tech_stack_breadth": 0, "complexity": 0,
                    "jd_relevance": 0, "overall_github_score": 0,
                    "explanation": "Could not evaluate any repositories.",
                    "mode": "portfolio"
                }

            # Average scores across evaluated repos
            avg = lambda key: round(sum(float(e.get(key, 0)) for e in repo_evaluations) / len(repo_evaluations), 1)
            code_quality = avg("code_quality")
            tech_stack = avg("tech_stack_breadth")
            complexity = avg("complexity")
            jd_relevance = avg("jd_relevance")
            overall = round((code_quality * 0.3 + tech_stack * 0.2 + complexity * 0.2 + jd_relevance * 0.3), 1)

            # Build portfolio summary
            portfolio_explanation = (
                f"Analyzed {len(repo_evaluations)} of {len(repos)} repositories "
                f"for {account_data.get('name', parsed['username'])}. "
                f"Total stars: {account_data.get('total_stars', 0)}. "
                f"Primary languages: {', '.join(list(account_data.get('all_languages', {}).keys())[:5])}."
            )

            return {
                "code_quality": code_quality,
                "tech_stack_breadth": tech_stack,
                "complexity": complexity,
                "jd_relevance": jd_relevance,
                "overall_github_score": overall,
                "explanation": portfolio_explanation,
                "mode": "portfolio",
                "portfolio_info": {
                    "username": parsed["username"],
                    "display_name": account_data.get("name", parsed["username"]),
                    "bio": account_data.get("bio", ""),
                    "total_repos": len(repos),
                    "total_stars": account_data.get("total_stars", 0),
                    "followers": account_data.get("followers", 0),
                    "all_languages": account_data.get("all_languages", {}),
                },
                "analyzed_repos": repo_evaluations,
            }

    except Exception as e:
        return {
            "code_quality": 0,
            "tech_stack_breadth": 0,
            "complexity": 0,
            "jd_relevance": 0,
            "overall_github_score": 0,
            "explanation": f"GitHub analysis failed: {str(e)}",
            "mode": "error"
        }
