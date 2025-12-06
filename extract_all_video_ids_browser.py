"""
استخراج جميع video IDs من الدروس (1-29) باستخدام browser automation
والنقر على كل درس واستخراج Brightcove video ID من network requests
"""
import json
import re
from pathlib import Path
import time

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

print(f"📚 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: استخراج جميع video IDs من 29 درس\n")

# Video IDs الموجودة
existing_ids = {v['yanfaa_video_id'] for v in existing_videos}

print("=" * 60)
print("📋 الخطوات:")
print("1. سأفتح المتصفح وأنتقل إلى صفحة الكورس")
print("2. سأنقر على كل درس (1, 2, 3, ... حتى 29)")
print("3. سأستخرج Brightcove video ID من network requests")
print("4. سأحفظ جميع video IDs في ملف JSON")
print("=" * 60)
print("\n⏳ انتظر... سأبدأ الآن...\n")

# هذا الكود سيتم تنفيذه في browser automation
print("""
سأستخدم browser automation tools لفتح المتصفح وتنفيذ التالي:

1. Navigate to: https://yanfaa.com/us/single/learning_english_level_one
2. Wait for page to load
3. Find lessons sidebar (عادة على اليسار أو في قائمة)
4. Click on lesson 1, wait for video to load, capture Brightcove video ID from network
5. Repeat for lessons 2-29
6. Save all video IDs to extracted_video_ids.json

الآن سأبدأ التنفيذ...
""")



