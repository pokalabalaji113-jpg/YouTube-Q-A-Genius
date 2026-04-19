"""
transcript.py - YouTube Transcript Extractor using yt-dlp
"""

import re
import json
import subprocess
import requests


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:shorts\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_metadata(video_id: str) -> dict:
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", "Unknown Title"),
                "author": data.get("author_name", "Unknown Channel"),
                "thumbnail": data.get("thumbnail_url", ""),
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
    except Exception:
        pass
    return {
        "title": "Unknown Title",
        "author": "Unknown Channel",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def get_transcript(video_id: str) -> dict:
    """Fetch transcript using yt-dlp — works even when YouTube blocks API calls."""
    import tempfile, os

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--write-sub",
            "--sub-lang", "en",
            "--sub-format", "json3",
            "--skip-download",
            "--no-playlist",
            "-o", f"{tmpdir}/sub",
            url
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=60)
        except Exception as e:
            return _error(str(e))

        # Find the downloaded subtitle file
        sub_file = None
        for f in os.listdir(tmpdir):
            if f.endswith(".json3"):
                sub_file = os.path.join(tmpdir, f)
                break

        if not sub_file:
            return _error("No captions found for this video. Make sure the video has subtitles/CC enabled.")

        with open(sub_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Parse json3 subtitle format
    segments = []
    for event in data.get("events", []):
        if "segs" not in event:
            continue
        text = "".join(s.get("utf8", "") for s in event["segs"]).strip()
        if not text or text == "\n":
            continue
        start_ms = event.get("tStartMs", 0)
        dur_ms = event.get("dDurationMs", 0)
        start_sec = start_ms / 1000
        segments.append({
            "text": text,
            "start": start_sec,
            "duration": dur_ms / 1000,
            "timestamp": format_timestamp(start_sec),
        })

    if not segments:
        return _error("Transcript was empty after parsing.")

    full_text = " ".join(s["text"] for s in segments)
    last = segments[-1]
    total_duration = last["start"] + last["duration"]

    return {
        "success": True,
        "text": full_text,
        "segments": segments,
        "word_count": len(full_text.split()),
        "duration_seconds": total_duration,
        "duration_formatted": format_timestamp(total_duration),
        "segment_count": len(segments),
    }


def _error(msg: str) -> dict:
    return {
        "success": False, "error": msg,
        "text": "", "segments": [],
        "word_count": 0, "duration_seconds": 0,
        "duration_formatted": "0:00", "segment_count": 0,
    }


def format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def chunk_transcript(transcript_data: dict, chunk_size: int = 1000, overlap: int = 200) -> list:
    text = transcript_data["text"]
    segments = transcript_data["segments"]
    words = text.split()
    chunks = []
    chunk_index = 0
    i = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunk_text = " ".join(chunk_words)
        char_position = len(" ".join(words[:i]))
        timestamp = get_timestamp_for_position(segments, char_position, len(text))
        chunks.append({
            "text": chunk_text,
            "chunk_index": chunk_index,
            "timestamp": timestamp,
            "word_start": i,
            "word_end": min(i + chunk_size, len(words)),
        })
        chunk_index += 1
        i += chunk_size - overlap
    return chunks


def get_timestamp_for_position(segments: list, char_pos: int, total_chars: int) -> str:
    if not segments:
        return "0:00"
    ratio = char_pos / max(total_chars, 1)
    idx = int(ratio * len(segments))
    idx = max(0, min(idx, len(segments) - 1))
    return segments[idx]["timestamp"]