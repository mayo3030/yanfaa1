"""
Complete script to extract all video IDs and then download them
This will be executed step by step via browser automation
"""
import json
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

print("="*60)
print("📋 Instructions for Browser Automation:")
print("="*60)
print("""
1. Navigate to: https://yanfaa.com/us/single/learning_english_level_one
2. For each lesson in the sidebar:
   - Click on the lesson
   - Wait 3 seconds for video to load
   - Check network requests for:
     - Yanfaa API: /api/videos/{id} or /api/promos/{id}
     - Brightcove API: /edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{id}
   - Extract both IDs
   - Save to extracted_video_ids.json
   - Continue to next lesson

3. After extracting all 29 video IDs:
   - Use the download script to download all videos

Progress: Currently have 12/29 videos extracted
""")
