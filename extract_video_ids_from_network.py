"""
استخراج video IDs من network requests
"""
import json
import re
from pathlib import Path

# Video IDs المستخرجة من network requests
found_videos = [
    {
        "yanfaa_video_id": 1136,
        "brightcove_video_id": "6247287755001",
        "title": "11- descreptions"
    },
    {
        "yanfaa_video_id": 1137,
        "brightcove_video_id": "6247290379001",
        "title": "12- clothes -colors"
    },
    {
        "yanfaa_video_id": 1138,
        "brightcove_video_id": "6247288259001",
        "title": "13- wearing and not wearing"
    },
    {
        "yanfaa_video_id": 1139,
        "brightcove_video_id": "6247290382001",
        "title": "14- excerise wearing-"
    },
    {
        "yanfaa_video_id": 1146,
        "brightcove_video_id": "6247297128001",
        "title": "21- Transportation"
    },
    {
        "yanfaa_video_id": 1149,
        "brightcove_video_id": "6247292063001",
        "title": "24- Family-"
    }
]

# حفظ البيانات
course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(found_videos, f, indent=2, ensure_ascii=False)

print(f"✅ تم حفظ {len(found_videos)} video IDs إلى {output_file}")
print("\n📹 Video IDs المستخرجة:")
for i, video in enumerate(found_videos, 1):
    print(f"{i}. [{video['yanfaa_video_id']}] {video['title']} - Brightcove: {video['brightcove_video_id']}")



