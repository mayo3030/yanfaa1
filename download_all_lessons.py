"""
Download all lessons by:
1. Monitoring network requests when clicking each lesson
2. Extracting Brightcove video IDs
3. Downloading each video using ffmpeg
"""
import json
import subprocess
import sys
from pathlib import Path
import httpx
import re

# Since the user can access lessons in browser, we'll:
# 1. Get course data (even if only shows 1 video in API)
# 2. Use browser automation to click each lesson
# 3. Capture video IDs from network requests
# 4. Download each video

# For now, let's try to find the video IDs from the course structure
# The API might return video_count: 29 but only shows 1 video
# Maybe there's a way to get all video IDs

session_id = 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM'
course_slug = 'learning_english_level_one'

print(f"📚 Course: {course_slug}")
print(f"🔑 Session: {session_id}\n")

# Try to get course structure
url = f'https://app.yanfaa.com/api/course/{course_slug}?session_id={session_id}'
headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}'
}

r = httpx.get(url, headers=headers)
data = r.json()

print(f"Course Title: {data.get('title')}")
print(f"Video Count (API): {data.get('video_count', 0)}")
print(f"Videos Returned: {len(data.get('videos', []))}")
print(f"Is Enrolled: {data.get('is_enrolled')}\n")

# The issue: API returns video_count: 29 but only 1 video in videos array
# This suggests the videos are loaded dynamically when you click on them

# Strategy: We need to use browser automation to:
# 1. Click on each lesson
# 2. Capture the Brightcove video ID from network requests
# 3. Build a list of all video IDs
# 4. Download each one

print("""
📋 Next Steps:
Since the browser shows all 29 lessons but API only returns 1,
we need to extract video IDs from browser network requests.

Would you like me to:
1. Create a browser automation script to click each lesson and capture video IDs?
2. Or can you manually open DevTools > Network tab and click through lessons
   while I monitor and extract the video IDs?

For now, let me check if there's another API endpoint that returns all videos...
""")

# Try alternative endpoints
alternatives = [
    f'https://app.yanfaa.com/api/course/{course_slug}/chapters',
    f'https://app.yanfaa.com/api/courses/{data.get("id")}/videos',
    f'https://app.yanfaa.com/api/auth/courseProgress/{data.get("id")}?session_id={session_id}',
]

for alt_url in alternatives:
    try:
        alt_r = httpx.get(alt_url, headers=headers, timeout=5)
        if alt_r.status_code == 200:
            print(f"✅ {alt_url}")
            alt_data = alt_r.json()
            if isinstance(alt_data, dict) and ('videos' in alt_data or 'lessons' in alt_data or 'chapters' in alt_data):
                print(f"   Found data structure: {list(alt_data.keys())}")
    except:
        pass



