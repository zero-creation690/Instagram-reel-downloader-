from flask import Flask, request, jsonify
from flask_cors import CORS
import instaloader
import re

app = Flask(__name__)
# This enables CORS for all routes and origins
CORS(app)

# Initialize Instaloader
L = instaloader.Instaloader()

@app.route('/api/download', methods=['GET'])
def get_reel_data():
    reel_url = request.args.get('url')
    
    if not reel_url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Extract shortcode from URL
    match = re.search(r"(?:/p/|/reel/|/tv/)([\w-]+)", reel_url)
    if not match:
        return jsonify({"error": "Invalid Instagram URL format"}), 400
        
    shortcode = match.group(1)

    try:
        # Get post metadata
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        if post.is_video:
            video_url = post.video_url
            # You could also include other details if needed
            response_data = {
                "success": True,
                "video_url": video_url,
                "caption": post.caption,
                "owner_username": post.owner_username,
                "thumbnail_url": post.url  # This is often the thumbnail
            }
            return jsonify(response_data)
        else:
            return jsonify({"error": "The provided URL is not a video/reel"}), 400

    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({"error": "Profile does not exist"}), 404
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        return jsonify({"error": "Cannot fetch from a private profile"}), 403
    except instaloader.exceptions.LoginRequiredException:
         return jsonify({"error": "Login is required to access this content"}), 403
    except Exception as e:
        # Generic error for other issues (e.g., post deleted, network error)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# This is the entry point for Vercel
# Vercel runs the 'app' variable by default
