"""
استخراج video IDs من network requests الحالية
"""
import json
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

# قراءة الفيديوهات الموجودة
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

# Video IDs من network requests
# من network requests الحالية، وجدنا:
found_from_network = [
    {"yanfaa_id": 1126, "brightcove_id": "6247279977001", "title": "01-intro"},
    {"yanfaa_id": 1127, "brightcove_id": "6247275935001", "title": "02 - alphabet"},
    {"yanfaa_id": 1125, "brightcove_id": "6253662723001", "title": "Promo - learning englesh level one new promo"},
    {"yanfaa_id": 1138, "brightcove_id": "6247288259001", "title": "13- wearing and not wearing"},
]

print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🔍 Video IDs من network requests: {len(found_from_network)}\n")

# دمج مع الفيديوهات الموجودة
all_videos_dict = {v['yanfaa_video_id']: v for v in existing_videos}

for video in found_from_network:
    if video['yanfaa_id'] not in all_videos_dict:
        all_videos_dict[video['yanfaa_id']] = {
            'yanfaa_video_id': video['yanfaa_id'],
            'brightcove_video_id': video['brightcove_id'],
            'title': video['title']
        }
        print(f"✅ أضيف: {video['title']} (ID: {video['yanfaa_id']})")

# تحويل إلى list وترتيب
all_videos_list = sorted(all_videos_dict.values(), key=lambda x: x['yanfaa_video_id'])

print(f"\n📊 النتائج:")
print(f"✅ إجمالي الفيديوهات: {len(all_videos_list)}")
print(f"🎯 الهدف: 29 درس\n")

# حفظ النتائج
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_videos_list, f, indent=2, ensure_ascii=False)

print("📋 قائمة جميع الفيديوهات:")
for i, video in enumerate(all_videos_list, 1):
    print(f"   {i:2d}. [{video['yanfaa_video_id']:4d}] {video['title']}")

print(f"\n💾 تم حفظ جميع video IDs في: {output_file}")

if len(all_videos_list) < 29:
    print(f"\n⚠️ لا تزال توجد {29 - len(all_videos_list)} فيديو مفقود")
    print("💡 استمر في النقر على باقي الدروس لاستخراج video IDs...")
else:
    print("\n✅ تم العثور على جميع الفيديوهات!")



