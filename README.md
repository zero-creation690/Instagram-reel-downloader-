Instagram Reel Downloader API
This is a simple, serverless backend API built with Python (Flask) and Instaloader and designed for deployment on Vercel. It fetches the direct video URL and metadata for a given public Instagram Reel URL.
🚀 Key Features
 * Serverless Deployment: Optimized for Vercel's Python runtime using the @vercel/python builder.
 * Direct URL Extraction: Uses instaloader to parse the Reel's shortcode and retrieve the direct .mp4 link.
 * CORS Enabled: Fully configured to allow requests from any origin (*), making it suitable for web applications (frontend clients).
⚠️ Important Warning
Disclaimer: Scraping Instagram, even public content, is against their Terms of Service (ToS). This API relies on the structure of Instagram's public data, which can change without notice, causing the API to break. Furthermore, excessive use may lead to the server IP (provided by Vercel) being rate-limited or blocked by Instagram. Use at your own risk.
💻 API Endpoint
The service exposes one primary endpoint:
Endpoint: /api/download
Method: GET
Query Parameter: url (The full URL of the Instagram Reel/Post)
Example Request
To download the data for a reel, send a GET request to your deployed Vercel URL:
https://[YOUR-VERCEL-URL]/api/download?url=[https://www.instagram.com/reel/DQHtJ4rknBV/](https://www.instagram.com/reel/DQHtJ4rknBV/)

Example Success Response (JSON)
{
  "success": true,
  "video_url": "[https://scontent-iad3-1.cdninstagram.com/o1/v/t2/.../AQNjwfCh9XjNIh31otRrIJ3014rn1cwTAW-7LnN_vJPivwDZBMclJxRxQUito97uYF-VTfWkj38wk_44lGGPocnbFO-cshsE0X_61RY.mp4](https://scontent-iad3-1.cdninstagram.com/o1/v/t2/.../AQNjwfCh9XjNIh31otRrIJ3014rn1cwTAW-7LnN_vJPivwDZBMclJxRxQUito97uYF-VTfWkj38wk_44lGGPocnbFO-cshsE0X_61RY.mp4)",
  "caption": "Real 🦅...",
  "owner_username": "4ryancrick",
  "thumbnail_url": "[https://scontent-iad3-1.cdninstagram.com/v/t51.2885-15/](https://scontent-iad3-1.cdninstagram.com/v/t51.2885-15/)..."
}

Error Responses
The API handles various errors, returning appropriate HTTP status codes:
| Status Code | Description |
|---|---|
| 400 | Missing url parameter or invalid URL format. |
| 403 | Content is private or requires login (Instaloader issue). |
| 404 | Post or Profile does not exist. |
| 500 | General server or Instaloader error. |
🛠 Project Structure
The project is structured to meet Vercel's requirements for a Python Serverless Function:
/
├── api/
│   └── index.py  # The main Flask application and API logic
├── requirements.txt  # Python dependencies (Flask, instaloader, flask-cors)
└── vercel.json  # Vercel configuration

🚀 Local Setup and Deployment
1. Local Development
 * Clone the Repository:
   git clone [your-repo-link]
cd instagram-reel-downloader

 * Install Dependencies:
   pip install -r requirements.txt

 * Run Locally (requires Flask):
   export FLASK_APP=api/index.py
flask run
# API will run at [http://127.0.0.1:5000/api/download](http://127.0.0.1:5000/api/download)

2. Vercel Deployment
 * Install Vercel CLI:
   npm install -g vercel

 * Log in to Vercel:
   vercel login

 * Deploy the Project:
   vercel

   Follow the prompts. Vercel automatically detects the vercel.json file and handles the Python build process.
📜 Configuration (vercel.json)
The vercel.json file explicitly maps all incoming requests to the api/index.py serverless function, which is required for Vercel to recognize the Python API route.
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}

