"""
Update extracted video IDs with new findings
"""
import json
from pathlib import Path

output_file = Path('output/learning_english_level_one/videos/extracted_video_ids.json')

# Read existing videos
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

# New videos found
new_videos = [
    {
        "yanfaa_video_id": 1128,
        "brightcove_video_id": "6247275283001",
        "title": "03-numbers 0-10"
    },
    {
        "yanfaa_video_id": 1130,
        "brightcove_video_id": "6247277819001",
        "title": "05 ask- sides"
    }
]

# Add new videos if not already present
for new_video in new_videos:
    if (new_video['brightcove_video_id'] not in existing_brightcove_ids and 
        new_video['yanfaa_video_id'] not in existing_yanfaa_ids):
        existing_videos.append(new_video)
        existing_brightcove_ids.add(new_video['brightcove_video_id'])
        existing_yanfaa_ids.add(new_video['yanfaa_video_id'])
        print(f"✅ Added: {new_video['title']} (Yanfaa ID: {new_video['yanfaa_video_id']})")

# Sort by yanfaa_video_id
existing_videos.sort(key=lambda x: x['yanfaa_video_id'])

# Save updated list
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(existing_videos, f, indent=2, ensure_ascii=False)

print(f"\n📊 Total videos: {len(existing_videos)}")
print(f"🎯 Target: 29 lessons")
print(f"📝 Remaining: {29 - len(existing_videos)}")



