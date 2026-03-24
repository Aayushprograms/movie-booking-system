from urllib.parse import urlparse, parse_qs


def get_youtube_embed_url(url: str | None):
    if not url:
        return None

    parsed = urlparse(url)

    # youtu.be/<video_id>
    if parsed.netloc == "youtu.be":
        video_id = parsed.path.strip("/")
        return f"https://www.youtube.com/embed/{video_id}" if video_id else None

    # youtube.com/watch?v=<video_id>
    if parsed.netloc in ("youtube.com", "www.youtube.com"):
        video_id = parse_qs(parsed.query).get("v", [None])[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else None

    return None