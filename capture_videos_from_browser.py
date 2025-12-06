"""
Since the user can see all lessons in browser sidebar but API only returns 1 video,
we need to extract video data from browser JavaScript state or network requests.

Strategy:
1. Monitor network requests when clicking each lesson
2. Extract Brightcove video IDs from API calls
3. Download each video

For now, we'll create a helper script and ask user to:
- Open DevTools > Network tab
- Click on each lesson (1, 2, 3, ...)
- We'll capture the video IDs from Brightcove API calls
"""

import json
from pathlib import Path

print("""
📋 Instructions to extract video IDs manually:

Since you can see all lessons in the sidebar, please:

1. Open Chrome/Firefox DevTools (Press F12)
2. Go to "Network" tab
3. Filter by "XHR" or "Fetch"
4. Click on Lesson 1 in the sidebar
5. Look for a request to: edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}
6. Copy the VIDEO_ID (the number after /videos/)
7. Repeat for all 29 lessons

OR, I can automate this using browser automation tools.
But first, let me check if we can get the data another way...

Actually, since you mentioned you can access lessons 1 and 3,
let me try to extract the video data by monitoring network requests
when we click on lessons using browser automation.

Would you like me to:
1. Use browser automation to click each lesson and capture video IDs? (Recommended)
2. Or do you prefer to manually extract them?
""")

# Save session info
session_data = {
    'session_id': 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM',
    'course_slug': 'learning_english_level_one',
    'course_id': 69,
    'total_videos': 29,
    'note': 'User can access all lessons in browser sidebar'
}

output_dir = Path('output') / 'learning_english_level_one'
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'session_info.json', 'w', encoding='utf-8') as f:
    json.dump(session_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved session info to {output_dir / 'session_info.json'}")



