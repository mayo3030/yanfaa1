"""
Download videos by monitoring browser network requests when clicking lessons.
This approach works because the browser has authenticated cookies that allow access
to all videos, even if the API returns is_enrolled: false.
"""
import json
from pathlib import Path

print("""
🎯 Strategy:

Since you can open Lesson 1 and Lesson 3 in the browser (same URL),
the videos are accessible via JavaScript. Here's the plan:

1. **Monitor Network Requests**: When you click on a lesson in the browser,
   there should be an API call or Brightcove request that loads the video.

2. **Extract Video URLs**: The HLS streaming URLs are in the network requests.
   We can download them directly using ffmpeg.

3. **Browser Automation**: I'll use browser automation to:
   - Click on each lesson (1, 2, 3, ...)
   - Capture the HLS URL from network requests
   - Download each video

Let me create a script that does this automatically...
""")

# Since the user can access videos in browser, we should:
# 1. Use browser to navigate and click each lesson
# 2. Extract HLS URLs from network requests
# 3. Download using ffmpeg

# For now, let's create a helper that uses the browser MCP tools to do this



