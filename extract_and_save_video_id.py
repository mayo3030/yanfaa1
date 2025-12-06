"""
Extract and save video ID from network requests
"""
import json
import re
from pathlib import Path

output_file = Path('output/learning_english_level_one/videos/extracted_video_ids.json')

# Load existing videos
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

# New video found
new_video = {
    "yanfaa_video_id": 1129,
    "brightcove_video_id": "6247275284001",
    "title": "04 A& AN&are yes and no"
}

if new_video['brightcove_video_id'] not in existing_brightcove_ids and new_video['yanfaa_video_id'] not in existing_yanfaa_ids:
    existing_videos.append(new_video)
    existing_brightcove_ids.add(new_video['brightcove_video_id'])
    existing_yanfaa_ids.add(new_video['yanfaa_video_id'])
    print(f"✅ Added: {new_video['title']} (Yanfaa ID: {new_video['yanfaa_video_id']})")
else:
    print(f"ℹ️ Video already exists: {new_video['title']}")

# Sort by yanfaa_video_id
existing_videos.sort(key=lambda x: x['yanfaa_video_id'])

# Save
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(existing_videos, f, indent=2, ensure_ascii=False)

print(f"\n📊 Total videos: {len(existing_videos)}")
print(f"🎯 Target: 29 lessons")
print(f"📝 Remaining: {29 - len(existing_videos)}")



