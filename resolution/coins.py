"""Coin economy configuration and utilities."""

from resolution import storage


# Coin rewards configuration
REWARDS = {
    "bible_chapter": 5,
    "bible_catchup_chapter": 3,
    "leetcode_easy": 10,
    "leetcode_medium": 25,
    "leetcode_hard": 50,
    "goal_completed": 15,
}


def get_balance() -> int:
    """Get current coin balance."""
    return storage.get_coins()


def award_bible_reading(chapters: int, is_catchup: bool = False) -> int:
    """Award coins for Bible reading. Returns coins awarded."""
    reward_type = "bible_catchup_chapter" if is_catchup else "bible_chapter"
    coins = chapters * REWARDS[reward_type]
    storage.add_coins(coins)
    return coins


def award_leetcode(difficulty: str) -> int:
    """Award coins for completing a LeetCode problem. Returns coins awarded."""
    key = f"leetcode_{difficulty.lower()}"
    coins = REWARDS.get(key, REWARDS["leetcode_easy"])
    storage.add_coins(coins)
    return coins


def award_goal_completed(count: int = 1) -> int:
    """Award coins for completing goals. Returns coins awarded."""
    coins = count * REWARDS["goal_completed"]
    storage.add_coins(coins)
    return coins


def get_reward_info() -> dict:
    """Get information about all reward types."""
    return REWARDS.copy()

