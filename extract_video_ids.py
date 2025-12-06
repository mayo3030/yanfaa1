"""
Extract video IDs by monitoring Brightcove API calls.
When a lesson is clicked, Brightcove API is called with the video ID.
We'll capture these from network requests.
"""
import json
import re
from pathlib import Path

print("""
🎯 Strategy to extract all video IDs:

Since clicking on a lesson triggers a Brightcove API call like:
https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}

We can:
1. Monitor network requests when clicking each lesson
2. Extract video IDs from Brightcove API URLs
3. Save all video IDs to a file
4. Download each video using ffmpeg

Let me create a script that uses browser automation to do this...
""")

# We'll need to:
# 1. Navigate to course page
# 2. Find the lessons list (sidebar)
# 3. Click each lesson one by one
# 4. Capture Brightcove video ID from network requests
# 5. Repeat for all 29 lessons

# For now, let's save the session and course info
session_id = 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM'
course_slug = 'learning_english_level_one'
course_id = 69

session_data = {
    'session_id': session_id,
    'course_slug': course_slug,
    'course_id': course_id,
    'total_videos': 29
}

output_dir = Path('output') / course_slug
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'session_info.json', 'w', encoding='utf-8') as f:
    json.dump(session_data, f, indent=2, ensure_ascii=False)

print(f"✅ Saved session info to {output_dir / 'session_info.json'}")

print("""
📌 Next: I'll create a browser automation script to:
1. Click on each lesson in the sidebar
2. Monitor network requests for Brightcove API calls
3. Extract all video IDs
4. Download each video

Let me create this script now...
""")



