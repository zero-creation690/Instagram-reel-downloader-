from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/api/reel")
def get_reel(url: str = Query(..., description="Instagram Reel URL")):
    try:
        # Basic validation
        if "instagram.com/reel/" not in url:
            return JSONResponse(
                {"success": False, "error": "Invalid Instagram reel URL"},
                status_code=400,
            )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return JSONResponse(
                {"success": False, "error": "Failed to fetch the reel page"},
                status_code=500,
            )

        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.find("meta", property="og:video") or soup.find("meta", property="og:video:secure_url")

        if not meta or not meta.get("content"):
            return JSONResponse(
                {"success": False, "error": "Video URL not found. Reel might be private or unavailable."},
                status_code=404,
            )

        video_url = meta["content"]
        return {"success": True, "video_url": video_url}

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
