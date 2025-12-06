"""
Automatically extract video IDs from all lessons by clicking through them
"""
import json
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

# Load existing videos
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

print("="*60)
print(f"🚀 Automatic Video ID Extraction")
print(f"📚 Course: {course_slug}")
print(f"📊 Existing videos: {len(existing_videos)}")
print(f"🎯 Target: 29 lessons")
print("="*60)

# Lesson elements from snapshot (from first list in محتوى الكورس)
lessons = [
    ("برومو", "ref-om6vq1x3mus"),
    ("Introduction", "ref-pji1kfk8t5c"),
    ("Le on 1", "ref-jixh7eccq9m"),
    ("Le on 2", "ref-nnd0ksjrfb"),
    ("Le on 3", "ref-2ohz3ew6dbu"),
    ("Le on 4", "ref-8jtsnzylpgo"),
    ("Le on 5", "ref-c4ejlkufenn"),
    ("Le on 6", "ref-x1u2imrf36j"),
    ("Le on 7", "ref-4heuo2e5q2"),
    ("Le on 8", "ref-z31uuka48k"),
    ("Le on 9", "ref-wnd2h0zp6yk"),
    ("Le on 10", "ref-oamk7jqagqm"),
    ("Le on 11", "ref-8uxmong7bvm"),
    ("Le on 12", "ref-r7vcdbq5d4"),
    ("Le on 13", "ref-ere19ks6m7d"),
    ("Le on 14", "ref-uuxxl2p0pen"),
    ("Le on 15", "ref-d09pvcsloct"),
    ("Le on 16", "ref-c9fpf7quxa8"),
    ("Le on 17", "ref-2udggtlzlf7"),
    ("Le on 18", "ref-nkyfq0j26xj"),
    ("Le on 19", "ref-sc2ar32a7cq"),
    ("Le on 20", "ref-5xmx4ryvkhv"),
    ("Le on 21", "ref-iprqckjo2z"),
    ("Le on 22", "ref-0bq1gzjwahb"),
    ("Le on 23", "ref-97ypwwzapn4"),
    ("Le on 24", "ref-vvs1q1rffsi"),
    ("Le on 25", "ref-auf1vd92v7a"),
    ("Le on 26", "ref-1mwa7w460jk"),
    ("Le on 27", "ref-wciu54egfu"),
    ("Le on 28", "ref-564yu9bda0q"),
]

print(f"\n📋 Found {len(lessons)} lessons to process\n")
print("⚠️  This script will be executed via browser automation tools.")
print("   Please run this through the browser automation interface.\n")

# Save the lesson list for reference
with open(output_dir / "lessons_list.json", 'w', encoding='utf-8') as f:
    json.dump(lessons, f, indent=2, ensure_ascii=False)

print(f"✅ Saved lesson list to {output_dir / 'lessons_list.json'}")
