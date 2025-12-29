"""LeetCode problem picker - daily coding practice."""

import json
import random
import webbrowser
from pathlib import Path

from resolution import storage


DATA_DIR = Path(__file__).parent.parent / "data"
LEETCODE_DATA_FILE = DATA_DIR / "leetcode_problems.json"

DIFFICULTY_MAP = {
    1: "Easy",
    2: "Medium", 
    3: "Hard",
}

DIFFICULTY_COINS = {
    "easy": 10,
    "medium": 25,
    "hard": 50,
}


def load_problems() -> list[dict]:
    """Load all LeetCode problems from the data file."""
    with open(LEETCODE_DATA_FILE, "r") as f:
        data = json.load(f)
    return data.get("stat_status_pairs", [])


def get_available_problems(difficulty: str) -> list[dict]:
    """Get available problems for a difficulty level that haven't been completed."""
    difficulty_level = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty.lower())
    if not difficulty_level:
        raise ValueError(f"Invalid difficulty: {difficulty}")
    
    all_problems = load_problems()
    completed_ids = storage.get_completed_leetcode_ids()
    
    available = []
    for problem in all_problems:
        # Skip paid-only problems
        if problem.get("paid_only"):
            continue
        
        # Skip hidden problems
        if problem.get("stat", {}).get("question__hide"):
            continue
        
        # Check difficulty
        if problem.get("difficulty", {}).get("level") != difficulty_level:
            continue
        
        # Skip completed problems
        question_id = problem.get("stat", {}).get("question_id")
        if question_id in completed_ids:
            continue
        
        available.append({
            "id": question_id,
            "frontend_id": problem.get("stat", {}).get("frontend_question_id"),
            "title": problem.get("stat", {}).get("question__title"),
            "slug": problem.get("stat", {}).get("question__title_slug"),
            "difficulty": DIFFICULTY_MAP.get(difficulty_level, "Unknown"),
        })
    
    return available


def get_random_problems(difficulty: str, count: int = 3) -> list[dict]:
    """Get random problems of a given difficulty."""
    available = get_available_problems(difficulty)
    if len(available) <= count:
        return available
    return random.sample(available, count)


def get_problem_url(slug: str) -> str:
    """Get the URL for a LeetCode problem."""
    return f"https://leetcode.com/problems/{slug}/"


def open_problem(slug: str) -> str:
    """Open a LeetCode problem in the browser. Returns the URL."""
    url = get_problem_url(slug)
    webbrowser.open(url)
    return url


def mark_problem_done(problem_id: int, difficulty: str) -> int:
    """Mark a problem as completed and return coins earned."""
    storage.mark_leetcode_completed(problem_id)
    coins = DIFFICULTY_COINS.get(difficulty.lower(), 10)
    storage.add_coins(coins)
    return coins


def get_stats() -> dict:
    """Get LeetCode completion stats."""
    all_problems = load_problems()
    completed_ids = storage.get_completed_leetcode_ids()
    
    stats = {
        "total_completed": len(completed_ids),
        "easy": {"completed": 0, "total": 0},
        "medium": {"completed": 0, "total": 0},
        "hard": {"completed": 0, "total": 0},
    }
    
    for problem in all_problems:
        if problem.get("paid_only") or problem.get("stat", {}).get("question__hide"):
            continue
        
        level = problem.get("difficulty", {}).get("level")
        difficulty = {1: "easy", 2: "medium", 3: "hard"}.get(level)
        if not difficulty:
            continue
        
        stats[difficulty]["total"] += 1
        
        question_id = problem.get("stat", {}).get("question_id")
        if question_id in completed_ids:
            stats[difficulty]["completed"] += 1
    
    return stats

