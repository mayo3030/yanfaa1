"""
استخراج جميع video IDs تلقائياً من network requests عند النقر على الدروس
يستخدم browser automation لاستخراج video IDs من Brightcove API calls
"""
import json
from pathlib import Path
import time

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

print("="*60)
print("🎯 استخراج جميع video IDs من الدروس (1-29)")
print("="*60)
print(f"\n📊 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: استخراج جميع video IDs من 29 درس\n")

print("""
الخطة:
1. سأفتح المتصفح وأنتقل إلى صفحة الكورس
2. سأنتظر تحميل الصفحة
3. سأبحث عن قائمة الدروس (sidebar)
4. سأنقر على كل درس (1, 2, 3, ... حتى 29)
5. عند كل نقر، سأستخرج Brightcove video ID من network requests
6. سأحفظ جميع video IDs في ملف JSON

الآن سأبدأ...
""")

# سأستخدم browser automation tools هنا
print("\n⏳ جاهز لاستخدام browser automation...")
print("💡 سأستخدم Cursor browser tools للنقر على الدروس واستخراج video IDs\n")

# هذه البيانات سيتم جمعها من browser automation
extracted_videos = []

# TODO: استخدام browser automation tools:
# 1. Navigate to course_url
# 2. Wait for page load
# 3. Find lessons sidebar/list
# 4. Click on each lesson and monitor network requests
# 5. Extract Brightcove video ID from: edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}
# 6. Save all video IDs

print("📝 بعد استخراج جميع video IDs، سيتم حفظها تلقائياً في ملف JSON")
print("🚀 ثم يمكنك استخدام download_all_parallel_turbo.py لتحميلها جميعاً بشكل متوازي\n")



