"""
utils.py - Helper Utilities
"""

import os
import re
import time
import streamlit as st


def format_duration(seconds: float) -> str:
    """Format seconds into human readable duration."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    else:
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{h}h {m}m {s}s"


def format_number(n: int) -> str:
    """Format large numbers with K/M suffix."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as filename."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:50]  # Limit length


def stream_text(text: str, placeholder, delay: float = 0.01):
    """Simulate streaming text output for better UX."""
    full_text = ""
    words = text.split(" ")
    for word in words:
        full_text += word + " "
        placeholder.markdown(full_text + "▋")
        time.sleep(delay)
    placeholder.markdown(full_text)


def check_api_keys() -> dict:
    """Check which API keys are configured."""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "provider": os.getenv("LLM_PROVIDER", "groq"),
    }


def get_youtube_embed_url(video_id: str) -> str:
    """Get YouTube embed URL for iframe display."""
    return f"https://www.youtube.com/embed/{video_id}"


def estimate_read_time(text: str) -> int:
    """Estimate reading time in minutes (avg 200 words/min)."""
    word_count = len(text.split())
    return max(1, word_count // 200)


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Truncate text to max_chars with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL."""
    youtube_patterns = [
        r"youtube\.com\/watch\?v=",
        r"youtu\.be\/",
        r"youtube\.com\/embed\/",
        r"youtube\.com\/shorts\/",
    ]
    return any(re.search(pattern, url) for pattern in youtube_patterns)


def get_session_stats(chat_history: list) -> dict:
    """Get stats about the current Q&A session."""
    user_messages = [m for m in chat_history if m["role"] == "user"]
    assistant_messages = [m for m in chat_history if m["role"] == "assistant"]
    
    total_words = sum(len(m["content"].split()) for m in assistant_messages)
    
    return {
        "questions_asked": len(user_messages),
        "total_responses": len(assistant_messages),
        "total_words": total_words,
        "avg_response_length": total_words // max(len(assistant_messages), 1),
    }