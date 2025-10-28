from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests, re

app = FastAPI()

@app.get("/api/reel")
def get_reel(url: str = Query(..., description="Instagram Reel URL")):
    try:
        if "instagram.com/reel/" not in url:
            return JSONResponse({"success": False, "error": "Invalid Instagram reel URL"}, status_code=400)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return JSONResponse({"success": False, "error": "Failed to fetch the reel page"}, status_code=500)

        match = re.search(r'"video_url":"([^"]+)"', response.text)
        if not match:
            return JSONResponse({"success": False, "error": "Video URL not found. Reel may be private."}, status_code=404)

        video_url = match.group(1).replace("\\u0026", "&")
        return {"success": True, "video_url": video_url}

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
