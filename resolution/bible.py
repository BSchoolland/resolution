"""Bible reading tracker - read through the Bible in one year."""

import json
from datetime import date, datetime
from pathlib import Path

from resolution import storage


# Load Bible chapter data
DATA_DIR = Path(__file__).parent.parent / "data"
BIBLE_DATA_FILE = DATA_DIR / "bible_chapters.json"

TOTAL_CHAPTERS = 1189
DAYS_IN_YEAR = 365


def load_bible_data() -> dict:
    """Load Bible chapter data."""
    with open(BIBLE_DATA_FILE, "r") as f:
        return json.load(f)


def get_daily_target() -> float:
    """Get the target chapters per day to complete in a year."""
    return TOTAL_CHAPTERS / DAYS_IN_YEAR  # ~3.26 chapters/day


def get_days_elapsed() -> int:
    """Get the number of days elapsed since the start date."""
    progress = storage.get_bible_progress()
    start = datetime.strptime(progress["start_date"], "%Y-%m-%d").date()
    today = date.today()
    
    if today < start:
        return 0
    
    return (today - start).days + 1  # +1 because day 1 is the first day


def get_expected_chapters() -> int:
    """Get the expected number of chapters to have read by today."""
    days = get_days_elapsed()
    return min(int(days * get_daily_target()), TOTAL_CHAPTERS)


def get_reading_status() -> dict:
    """Get the current reading status."""
    progress = storage.get_bible_progress()
    chapters_read = progress["chapters_read"]
    expected = get_expected_chapters()
    days_elapsed = get_days_elapsed()
    
    # Calculate today's reading assignment
    daily_target = get_daily_target()
    chapters_today = int((days_elapsed * daily_target) - ((days_elapsed - 1) * daily_target))
    chapters_today = max(3, min(4, chapters_today))  # Usually 3 or 4 per day
    
    behind = expected - chapters_read
    
    return {
        "chapters_read": chapters_read,
        "expected": expected,
        "total": TOTAL_CHAPTERS,
        "behind": max(0, behind),
        "ahead": max(0, -behind),
        "chapters_today": chapters_today,
        "days_elapsed": days_elapsed,
        "percent_complete": round((chapters_read / TOTAL_CHAPTERS) * 100, 1),
    }


def get_current_position() -> dict:
    """Get the current book and chapter being read."""
    progress = storage.get_bible_progress()
    chapters_read = progress["chapters_read"]
    
    bible_data = load_bible_data()
    books = bible_data["books"]
    
    cumulative = 0
    for book in books:
        if cumulative + book["chapters"] > chapters_read:
            chapter_in_book = chapters_read - cumulative + 1
            return {
                "book": book["name"],
                "chapter": chapter_in_book,
                "chapters_in_book": book["chapters"],
            }
        cumulative += book["chapters"]
    
    # Completed the Bible
    return {
        "book": "Revelation",
        "chapter": 22,
        "chapters_in_book": 22,
        "complete": True,
    }


def get_todays_reading() -> list[str]:
    """Get a list of chapters to read today."""
    status = get_reading_status()
    position = get_current_position()
    
    if position.get("complete"):
        return ["You've completed the Bible! 🎉"]
    
    bible_data = load_bible_data()
    books = bible_data["books"]
    
    readings = []
    chapters_to_read = status["chapters_today"]
    
    current_book = position["book"]
    current_chapter = position["chapter"]
    
    # Find the current book index
    book_idx = 0
    for i, book in enumerate(books):
        if book["name"] == current_book:
            book_idx = i
            break
    
    chapters_remaining = chapters_to_read
    while chapters_remaining > 0 and book_idx < len(books):
        book = books[book_idx]
        chapters_left_in_book = book["chapters"] - current_chapter + 1
        
        chapters_from_this_book = min(chapters_remaining, chapters_left_in_book)
        
        if chapters_from_this_book == 1:
            readings.append(f"{book['name']} {current_chapter}")
        else:
            end_chapter = current_chapter + chapters_from_this_book - 1
            readings.append(f"{book['name']} {current_chapter}-{end_chapter}")
        
        chapters_remaining -= chapters_from_this_book
        book_idx += 1
        current_chapter = 1
    
    return readings


def record_reading(chapters: int) -> dict:
    """Record chapters read and return updated status."""
    new_total = storage.add_bible_chapters(chapters)
    return get_reading_status()

