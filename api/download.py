# api/download.py
from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re
import json

app = FastAPI(title="Instagram Downloader API", version="2.0")

# ✅ Enable CORS for all (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

async def fetch_html(url: str) -> str:
    """Fetch page HTML from Instagram."""
    if not url.startswith("http"):
        url = "https://" + url
    # Convert to standard post URL for reels or short URLs
    url = re.sub(r"(reel|tv|stories)", "p", url)
    async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        return r.text

def extract_media_from_html(html: str) -> Optional[dict]:
    """Extract image/video URL from public Instagram HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Try <meta property="og:video">
    og_video = soup.find("meta", property="og:video")
    if og_video and og_video.get("content"):
        return {"url": og_video["content"], "type": "video"}

    # Try <meta property="og:image">
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return {"url": og_image["content"], "type": "image"}

    # Try JSON data inside <script type="application/ld+json">
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string)
            if isinstance(data, dict) and data.get("video"):
                video = data["video"]
                if isinstance(video, dict) and video.get("contentUrl"):
                    return {"url": video["contentUrl"], "type": "video"}
            elif isinstance(data, dict) and data.get("image"):
                img = data["image"]
                if isinstance(img, str):
                    return {"url": img, "type": "image"}
        except Exception:
            continue

    # Fallback: search for window.__sharedData
    text = soup.prettify()
    m = re.search(r'window\._sharedData\s*=\s*({.+?});', text)
    if m:
        try:
            jd = json.loads(m.group(1))
            media = jd.get("entry_data", {}).get("PostPage", [{}])[0].get("graphql", {}).get("shortcode_media")
            if media:
                if media.get("is_video"):
                    return {"url": media.get("video_url"), "type": "video"}
                else:
                    return {"url": media.get("display_url"), "type": "image"}
        except Exception:
            pass

    return None


@app.get("/api/info")
async def info(url: str = Query(..., description="Public Instagram post or reel URL")):
    """
    Returns JSON with direct media URL and type (image or video).
    Works for Posts, Reels, and TV videos.
    """
    try:
        html = await fetch_html(url)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error fetching URL: {e}")

    media = extract_media_from_html(html)
    if not media:
        raise HTTPException(
            status_code=404,
            detail="No media found. This may be a private post or Instagram structure changed."
        )
    return {"media_url": media["url"], "type": media["type"], "success": True}


@app.get("/api/fetch")
async def fetch_media(url: str = Query(..., description="Public Instagram post or reel URL")):
    """
    Proxies the media directly (downloads Reels, Posts, or TV videos).
    """
    try:
        html = await fetch_html(url)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error fetching URL: {e}")

    media = extract_media_from_html(html)
    if not media:
        raise HTTPException(status_code=404, detail="No media found (private or broken).")

    media_url = media["url"]

    try:
        async with httpx.AsyncClient(timeout=60.0, headers={"User-Agent": USER_AGENT}) as client:
            r = await client.get(media_url, follow_redirects=True)
            r.raise_for_status()
            content_type = r.headers.get("Content-Type", "video/mp4" if media["type"] == "video" else "image/jpeg")
            return Response(content=r.content, media_type=content_type)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error fetching media: {e}")
