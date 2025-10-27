from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import re
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def info_root():
    return {"message": "Reel Info API"}

@app.get("/api/info")
async def get_reel_info(url: str):
    """Get detailed information about an Instagram reel"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(url)
        response.raise_for_status()
        
        html_content = response.text
        
        # Extract JSON data
        json_pattern = r'window\._sharedData\s*=\s*({.+?});'
        match = re.search(json_pattern, html_content)
        
        if match:
            json_data = json.loads(match.group(1))
            posts = json_data['entry_data'].get('PostPage', [])
            
            if posts:
                media = posts[0].get('graphql', {}).get('shortcode_media', {})
                
                return {
                    'success': True,
                    'data': {
                        'id': media.get('id'),
                        'shortcode': media.get('shortcode'),
                        'is_video': media.get('is_video'),
                        'video_url': media.get('video_url'),
                        'display_url': media.get('display_url'),
                        'video_duration': media.get('video_duration'),
                        'dimensions': media.get('dimensions'),
                        'owner': {
                            'username': media.get('owner', {}).get('username'),
                            'full_name': media.get('owner', {}).get('full_name')
                        },
                        'caption': media.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''),
                        'timestamp': media.get('taken_at_timestamp'),
                        'likes': media.get('edge_media_preview_like', {}).get('count'),
                        'comments': media.get('edge_media_to_parent_comment', {}).get('count')
                    }
                }
        
        return {'success': False, 'error': 'No data found'}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
