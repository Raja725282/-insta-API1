import os
from flask import Flask, render_template, request, jsonify
from playwright.sync_api import sync_playwright
import random

app = Flask(__name__)

# List of User-Agents for randomization (you can extend this list)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    # Add more user agents as needed
]

def fetch_instagram_data(instagram_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=random.choice(USER_AGENTS))
        page.goto(instagram_url, timeout=100000)  # Increase timeout if necessary

        try:
            print("Page loaded successfully.")
            page.wait_for_selector("video", timeout=30000)  # Wait for the video element

            # Log the page content for debugging
            page_content = page.content()
            print(f"Raw page content: {page_content[:500]}...")  # Log the first 500 characters of the page content
            print(f"Raw page response: {page_content}")  # Log the raw response from the page

            # Fetch the video URL
            video_url = page.query_selector("video").get_attribute("src")

            # Fetch the thumbnail URL from meta tag (not visible)
            thumbnail_element = page.query_selector("meta[property='og:image']")
            thumbnail_url = thumbnail_element.get_attribute("content") if thumbnail_element else None

            # If the URLs are not found, raise an error
            if not video_url or not thumbnail_url:
                print("Error: Video or Thumbnail URL not found.")
                raise Exception("Failed to fetch video or thumbnail URL.")
            
            print(f"Fetched Video URL: {video_url}")  # Log the video URL
            print(f"Fetched Thumbnail URL: {thumbnail_url}")

        except Exception as e:
            print(f"Error fetching Instagram data: {e}")
            return {"error": str(e)}

        browser.close()
        return {"video_url": video_url, "thumbnail_url": thumbnail_url}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required!"})
    
    result = fetch_instagram_data(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
