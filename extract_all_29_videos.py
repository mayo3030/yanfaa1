"""
استخراج جميع video IDs من 29 درس تلقائياً
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

print("="*60)
print(f"📚 استخراج جميع video IDs للكورس: {course_slug}")
print(f"📊 الفيديوهات الموجودة حالياً: {len(existing_videos)}")
print(f"🎯 الهدف: 29 درس")
print("="*60)

# إضافة الفيديو الجديد الذي تم اكتشافه
new_video = {
    "yanfaa_video_id": 1128,
    "brightcove_video_id": "6247275283001",
    "title": "03-numbers 0-10"
}

if new_video['brightcove_video_id'] not in existing_brightcove_ids and new_video['yanfaa_video_id'] not in existing_yanfaa_ids:
    existing_videos.append(new_video)
    existing_brightcove_ids.add(new_video['brightcove_video_id'])
    existing_yanfaa_ids.add(new_video['yanfaa_video_id'])
    print(f"✅ تم إضافة: {new_video['title']} (Yanfaa ID: {new_video['yanfaa_video_id']})")

# قائمة الدروس التي يجب النقر عليها
# من snapshot، لدينا: برومو، Introduction، Le on 1-28
lessons_to_extract = [
    # الدروس الموجودة بالفعل (نحتاج فقط للتحقق)
    ("برومو", "ref-emvumly18ev", None),  # موجود: 1125
    ("Introduction", "ref-i3010rpsbma", None),  # موجود: 1126
    ("Le on 1", "ref-8a3b3dib80o", None),  # موجود: 1127
    ("Le on 2", "ref-33xijpewxot", None),  # موجود: 1128
    ("Le on 3", "ref-0om6evp0362", None),  # موجود: 1136
    ("Le on 11", "ref-5t1wfw62l2b", None),  # موجود: 1136 (11- descriptions)
    ("Le on 12", "ref-pylqj20tzzi", None),  # موجود: 1137
    ("Le on 13", "ref-563pkne7glk", None),  # موجود: 1138
    ("Le on 14", "ref-o7t6zlab1u", None),  # موجود: 1139
    ("Le on 21", "ref-5meuxoi1s3t", None),  # موجود: 1146
    ("Le on 24", "ref-t8ru38j64bo", None),  # موجود: 1149
    # الدروس المفقودة التي يجب استخراجها
    ("Le on 4", "ref-828i2wbxg3q", None),
    ("Le on 5", "ref-nxaxb62nay", None),
    ("Le on 6", "ref-t7uxszj3ml", None),
    ("Le on 7", "ref-rxmlok9vnu", None),
    ("Le on 8", "ref-nvqwn4zu32d", None),
    ("Le on 9", "ref-j675gorisro", None),
    ("Le on 10", "ref-dcr2rj8j5tl", None),
    ("Le on 15", "ref-yjm9a1e6uel", None),
    ("Le on 16", "ref-kd1nwzi1bz", None),
    ("Le on 17", "ref-sxcric8g4ob", None),
    ("Le on 18", "ref-zhj5xiuplm", None),
    ("Le on 19", "ref-tl10yken1h9", None),
    ("Le on 20", "ref-q1d2vzo4go9", None),
    ("Le on 22", "ref-ugjjtv87ic", None),
    ("Le on 23", "ref-4dcangublkj", None),
    ("Le on 25", "ref-luabxmkqcj", None),
    ("Le on 26", "ref-mng2m58lx7", None),
    ("Le on 27", "ref-4dtp4jvj2k3", None),
    ("Le on 28", "ref-a3ss660g2u6", None),
]

print(f"\n📋 الدروس المتبقية للاستخراج: {len([l for l in lessons_to_extract if l[2] is None])}")
print(f"💾 سيتم حفظ النتائج في: {output_file}\n")

# حفظ النتائج الحالية
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sorted(existing_videos, key=lambda x: x['yanfaa_video_id']), f, indent=2, ensure_ascii=False)

print(f"✅ تم حفظ {len(existing_videos)} فيديو حتى الآن")
if len(existing_videos) < 29:
    print(f"⚠️ لا يزال {29 - len(existing_videos)} فيديو مفقود")
    print("\n💡 استخدم browser automation tools للنقر على الدروس المتبقية:")
    for lesson_name, ref, _ in lessons_to_extract:
        if ref not in [v.get('ref') for v in existing_videos if 'ref' in v]:
            print(f"   - {lesson_name} ({ref})")


