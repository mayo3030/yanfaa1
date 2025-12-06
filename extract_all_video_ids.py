"""
Extract all video IDs from Brightcove API calls when navigating through lessons.

The strategy:
1. Monitor network requests when clicking each lesson
2. Extract video IDs from Brightcove API URLs:
   https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}
3. Save all video IDs to a JSON file
4. Download each video using the extracted IDs

For now, we found one video ID: 6253662723001 (promo video)

We need to click on each of the 29 lessons and extract their video IDs.
"""
import json
import re
from pathlib import Path

# Found video ID from network requests
found_video_id = "6253662723001"

course_slug = 'learning_english_level_one'
session_id = 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM'

output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# Save what we found so far
video_ids = {
    'promo': found_video_id,
    'lessons': [],  # Will be filled as we click through lessons
    'total_expected': 29,
    'course_slug': course_slug,
    'session_id': session_id
}

video_ids_file = output_dir / 'all_video_ids.json'
with open(video_ids_file, 'w', encoding='utf-8') as f:
    json.dump(video_ids, f, indent=2, ensure_ascii=False)

print(f"✅ Saved initial video ID to {video_ids_file}")
print(f"📹 Found video ID (promo): {found_video_id}")
print(f"\n📋 Next steps:")
print(f"1. Click on each lesson in the browser sidebar")
print(f"2. Monitor network requests for Brightcove API calls")
print(f"3. Extract video IDs from URLs like:")
print(f"   https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{{VIDEO_ID}}")
print(f"4. We'll collect all 29 video IDs")
print(f"\n💡 Tip: The video ID is the number at the end of the Brightcove URL")



