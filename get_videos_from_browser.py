"""
Since the user can access lessons in browser, we'll:
1. Use browser automation to click on each lesson
2. Monitor network requests to capture Brightcove video IDs
3. Download each video using the captured HLS URLs

For now, let's first try to get the video list by:
- Checking if there's a JavaScript object/array with all video data
- Or clicking through lessons and capturing video IDs
"""
import json

# The user said they can open lesson 1 and 3 in browser
# This means the data is in the browser's JavaScript state

# Let's create a simple script that will:
# 1. Navigate to course page
# 2. Click Chapter button
# 3. Extract lesson list
# 4. Click each lesson and capture video ID
# 5. Download videos

print("""
📌 Plan:

I'll use browser automation to:
1. Go to course page
2. Click "Chapter" to see all lessons  
3. Extract lesson data from DOM or network requests
4. For each lesson, click it and capture the Brightcove video ID
5. Download each video using ffmpeg

Since this requires interactive browser automation, 
let me check if we can get the data another way first...

Actually, since you mentioned you can open lessons 1 and 3, 
can you tell me:
- When you click on a lesson, does the video change?
- Does the URL change?
- Can you see a lesson list somewhere?

This will help me understand how to extract the data.
""")



