"""
Script to extract video information from browser network requests
This will monitor network requests when you interact with the course page
"""
import json
from pathlib import Path

print("""
🔍 To extract video information from the browser:

1. Open Chrome/Firefox Developer Tools (F12)
2. Go to Network tab
3. Navigate to: https://yanfaa.com/us/single/learning_english_level_one
4. Click on "Chapter" button to see all lessons
5. Click on Lesson 1, then Lesson 3
6. Look for API calls that return video data (filter by XHR/Fetch)
7. Copy the response JSON and save it here

Alternatively, I can use browser automation to capture this.
Let me create a script to do that automatically...
""")



