"""
استخراج جميع video IDs من خلال النقر على جميع الدروس باستخدام browser automation
"""
import json
import re
from pathlib import Path

# Note: This script should be run interactively with browser automation tools
# The browser functions are called via MCP tools, not as Python functions

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

print("="*60)
print("📋 دليل استخراج جميع video IDs")
print("="*60)
print("""
هذا السكريبت سيساعدك في استخراج جميع video IDs من خلال:

1. فتح صفحة الكورس في المتصفح
2. العثور على جميع عناصر الدروس
3. النقر على كل درس تلقائياً
4. استخراج video IDs من network requests
5. حفظ جميع النتائج في ملف JSON

⚠️ ملاحظة: يجب استخدام browser automation tools مباشرة
من خلال Cursor IDE للتنفيذ الفعلي.

📌 الخطوات:
1. تأكد أنك مسجل الدخول في المتصفح
2. افتح صفحة الكورس: https://yanfaa.com/us/single/learning_english_level_one
3. استخدم browser snapshot للعثور على عناصر الدروس
4. استخدم browser click للنقر على كل درس
5. استخدم browser network_requests لاستخراج video IDs
""")

# قراءة الفيديوهات الموجودة
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

print(f"\n📊 الفيديوهات الموجودة حالياً: {len(existing_videos)}")
print(f"🎯 الهدف: 29 درس\n")

if existing_videos:
    print("📋 الفيديوهات الحالية:")
    for i, video in enumerate(existing_videos, 1):
        print(f"   {i:2d}. [{video['yanfaa_video_id']:4d}] {video['title']}")

print(f"\n💡 للحصول على باقي الفيديوهات، استمر في النقر على الدروس.")
print(f"💾 سيتم حفظ النتائج في: {output_file}")



