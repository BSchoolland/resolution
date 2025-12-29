"""Storage module for JSON persistence in ~/.config/resolution/."""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any


CONFIG_DIR = Path.home() / ".config" / "resolution"
STATE_FILE = CONFIG_DIR / "state.json"
GOALS_FILE = CONFIG_DIR / "goals.json"
SHOP_FILE = CONFIG_DIR / "shop_items.json"


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default: Any = None) -> Any:
    """Load JSON from a file, returning default if not found."""
    if not path.exists():
        return default if default is not None else {}
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    """Save data to a JSON file."""
    ensure_config_dir()
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ─── State Management ───────────────────────────────────────────────────────


def get_state() -> dict:
    """Get the current state."""
    default_state = {
        "last_run_date": None,
        "coins": 0,
        "completed_leetcode_ids": [],
        "bible_chapters_read": 0,
        "start_date": "2026-01-01",
    }
    state = _load_json(STATE_FILE, default_state)
    # Merge with defaults for any missing keys
    for key, value in default_state.items():
        if key not in state:
            state[key] = value
    return state


def save_state(state: dict) -> None:
    """Save the state."""
    _save_json(STATE_FILE, state)


def ran_today() -> bool:
    """Check if the program has already run today."""
    state = get_state()
    last_run = state.get("last_run_date")
    if not last_run:
        return False
    return last_run == str(date.today())


def mark_ran_today() -> None:
    """Mark that the program ran today."""
    state = get_state()
    state["last_run_date"] = str(date.today())
    save_state(state)


def get_coins() -> int:
    """Get current coin balance."""
    return get_state().get("coins", 0)


def add_coins(amount: int) -> int:
    """Add coins and return new balance."""
    state = get_state()
    state["coins"] = state.get("coins", 0) + amount
    save_state(state)
    return state["coins"]


def spend_coins(amount: int) -> bool:
    """Spend coins if balance is sufficient. Returns True if successful."""
    state = get_state()
    current = state.get("coins", 0)
    if current < amount:
        return False
    state["coins"] = current - amount
    save_state(state)
    return True


# ─── Goals Management ───────────────────────────────────────────────────────


def get_todays_goals() -> list[str]:
    """Get today's goals."""
    data = _load_json(GOALS_FILE, {"date": None, "goals": []})
    if data.get("date") != str(date.today()):
        return []
    return data.get("goals", [])


def save_todays_goals(goals: list[str]) -> None:
    """Save today's goals."""
    _save_json(GOALS_FILE, {"date": str(date.today()), "goals": goals})


# ─── Shop Items Management ──────────────────────────────────────────────────


def get_shop_items() -> list[dict]:
    """Get all shop items."""
    return _load_json(SHOP_FILE, [])


def save_shop_items(items: list[dict]) -> None:
    """Save shop items."""
    _save_json(SHOP_FILE, items)


def add_shop_item(name: str, cost: int) -> dict:
    """Add a new shop item."""
    items = get_shop_items()
    item = {"id": len(items) + 1, "name": name, "cost": cost, "purchased": False}
    items.append(item)
    save_shop_items(items)
    return item


def update_shop_item(item_id: int, name: str = None, cost: int = None) -> bool:
    """Update a shop item. Returns True if found and updated."""
    items = get_shop_items()
    for item in items:
        if item["id"] == item_id:
            if name is not None:
                item["name"] = name
            if cost is not None:
                item["cost"] = cost
            save_shop_items(items)
            return True
    return False


def delete_shop_item(item_id: int) -> bool:
    """Delete a shop item. Returns True if found and deleted."""
    items = get_shop_items()
    original_len = len(items)
    items = [item for item in items if item["id"] != item_id]
    if len(items) < original_len:
        save_shop_items(items)
        return True
    return False


def purchase_shop_item(item_id: int) -> tuple[bool, str]:
    """Purchase a shop item. Returns (success, message)."""
    items = get_shop_items()
    for item in items:
        if item["id"] == item_id:
            if item.get("purchased"):
                return False, "Item already purchased!"
            if not spend_coins(item["cost"]):
                return False, f"Not enough coins! Need {item['cost']}, have {get_coins()}"
            item["purchased"] = True
            save_shop_items(items)
            return True, f"Purchased {item['name']}!"
    return False, "Item not found"


# ─── LeetCode Tracking ──────────────────────────────────────────────────────


def get_completed_leetcode_ids() -> set[int]:
    """Get set of completed LeetCode problem IDs."""
    state = get_state()
    return set(state.get("completed_leetcode_ids", []))


def mark_leetcode_completed(problem_id: int) -> None:
    """Mark a LeetCode problem as completed."""
    state = get_state()
    completed = state.get("completed_leetcode_ids", [])
    if problem_id not in completed:
        completed.append(problem_id)
        state["completed_leetcode_ids"] = completed
        save_state(state)


# ─── Bible Reading Tracking ─────────────────────────────────────────────────


def get_bible_progress() -> dict:
    """Get Bible reading progress."""
    state = get_state()
    return {
        "chapters_read": state.get("bible_chapters_read", 0),
        "start_date": state.get("start_date", "2026-01-01"),
    }


def add_bible_chapters(count: int) -> int:
    """Add chapters read and return new total."""
    state = get_state()
    state["bible_chapters_read"] = state.get("bible_chapters_read", 0) + count
    save_state(state)
    return state["bible_chapters_read"]

