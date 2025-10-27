from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import re
import json
from typing import Dict, Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InstagramReelDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_reel_info(self, url: str) -> Dict[str, Any]:
        """Extract reel information from Instagram URL"""
        try:
            # Clean the URL
            url = url.split('?')[0]
            
            # Fetch the page content
            response = self.session.get(url)
            response.raise_for_status()
            
            # Find JSON data in the HTML
            html_content = response.text
            
            # Look for JSON data in script tags
            json_pattern = r'window\._sharedData\s*=\s*({.+?});'
            match = re.search(json_pattern, html_content)
            
            if match:
                json_data = json.loads(match.group(1))
                return self._parse_json_data(json_data)
            
            # Alternative pattern for newer Instagram versions
            alternative_pattern = r'{"config":{"csrf_token":"[^"]+","viewer"[^>]+}'
            matches = re.findall(alternative_pattern, html_content)
            
            for match in matches:
                try:
                    json_data = json.loads(match)
                    return self._parse_json_data(json_data)
                except:
                    continue
            
            # If no JSON found, try to extract from meta tags
            return self._extract_from_meta_tags(html_content, url)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching reel: {str(e)}")

    def _parse_json_data(self, json_data: Dict) -> Dict[str, Any]:
        """Parse Instagram JSON data to extract reel information"""
        try:
            # Navigate through the JSON structure to find the video
            if 'entry_data' in json_data:
                posts = json_data['entry_data'].get('PostPage', [])
                if posts:
                    media = posts[0].get('graphql', {}).get('shortcode_media', {})
                    return self._extract_from_media(media)
            
            # Alternative path for different JSON structure
            if 'config' in json_data and 'viewer' in json_data.get('config', {}):
                # This might be a different structure, try to find video URLs
                pass
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing data: {str(e)}")
        
        raise HTTPException(status_code=404, detail="No reel data found")

    def _extract_from_media(self, media: Dict) -> Dict[str, Any]:
        """Extract information from media object"""
        is_video = media.get('is_video', False)
        
        if not is_video:
            raise HTTPException(status_code=400, detail="URL is not a video reel")
        
        video_url = media.get('video_url')
        if not video_url:
            raise HTTPException(status_code=404, detail="Video URL not found")
        
        return {
            'success': True,
            'type': 'reel',
            'url': video_url,
            'thumbnail': media.get('display_url'),
            'duration': media.get('video_duration'),
            'dimensions': {
                'width': media.get('dimensions', {}).get('width'),
                'height': media.get('dimensions', {}).get('height')
            },
            'owner': {
                'username': media.get('owner', {}).get('username'),
                'full_name': media.get('owner', {}).get('full_name')
            },
            'caption': media.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''),
            'timestamp': media.get('taken_at_timestamp')
        }

    def _extract_from_meta_tags(self, html: str, original_url: str) -> Dict[str, Any]:
        """Extract video URL from meta tags as fallback"""
        try:
            # Look for video URL in meta tags
            video_pattern = r'"video_url":"([^"]+)"'
            video_match = re.search(video_pattern, html)
            
            if video_match:
                video_url = video_match.group(1).replace('\\u0025', '%')
                return {
                    'success': True,
                    'type': 'reel',
                    'url': video_url,
                    'thumbnail': None,
                    'duration': None,
                    'dimensions': None,
                    'owner': {'username': 'unknown', 'full_name': 'unknown'},
                    'caption': '',
                    'timestamp': None
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not extract video: {str(e)}")
        
        raise HTTPException(status_code=404, detail="No video found in the page")

@app.get("/")
async def root():
    return {"message": "Instagram Reel Downloader API", "status": "active"}

@app.get("/api/download")
async def download_reel(url: str = None):
    """Download Instagram reel - returns direct download URL"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    if 'instagram.com' not in url:
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")
    
    downloader = InstagramReelDownloader()
    reel_info = downloader.get_reel_info(url)
    
    if reel_info['success']:
        # Return the direct download URL
        return JSONResponse({
            'success': True,
            'data': reel_info
        })
    else:
        raise HTTPException(status_code=404, detail="Reel not found")

@app.get("/api/info")
async def get_reel_info(url: str = None):
    """Get reel information without downloading"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    if 'instagram.com' not in url:
        raise HTTPException(status_code=400, detail="Invalid Instagram URL")
    
    downloader = InstagramReelDownloader()
    reel_info = downloader.get_reel_info(url)
    
    return JSONResponse(reel_info)

@app.get("/api/redirect")
async def redirect_to_download(url: str = None):
    """Redirect directly to the video file"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    downloader = InstagramReelDownloader()
    reel_info = downloader.get_reel_info(url)
    
    if reel_info['success']:
        return RedirectResponse(url=reel_info['url'])
    else:
        raise HTTPException(status_code=404, detail="Reel not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
