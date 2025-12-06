"""
استخراج جميع video IDs من network requests عند النقر على الدروس
هذا script يحتاج إلى أن تفتح DevTools > Network tab وتنقر على كل درس
"""
import json
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

print("="*60)
print("📋 تعليمات استخراج جميع video IDs:")
print("="*60)
print("""
1. افتح المتصفح واذهب إلى: https://yanfaa.com/us/single/learning_english_level_one
2. افتح DevTools (اضغط F12)
3. اذهب إلى تبويب "Network" (الشبكة)
4. قم بتصفية البحث بـ: "brightcove" أو "edge.api.brightcove.com"
5. انقر على كل درس في القائمة الجانبية (1, 2, 3, ... حتى 29)
6. عند النقر على كل درس، ستظهر طلبات API إلى Brightcove
7. ابحث عن URL يحتوي على: /videos/{VIDEO_ID}
8. انسخ VIDEO_ID (الرقم الطويل)
9. بعد الانتهاء من جميع الدروس، أضفها أدناه في القائمة

أو استخدم هذا الكود JavaScript في Console لاستخراجها تلقائياً:

```javascript
// استخراج video IDs من network requests
let videoIds = [];
let networkRequests = performance.getEntriesByType('resource');
networkRequests.forEach(req => {
    let match = req.name.match(/\\/videos\\/(\\d+)/);
    if (match) {
        let videoId = match[1];
        if (!videoIds.includes(videoId)) {
            videoIds.push(videoId);
        }
    }
});
console.log('Found video IDs:', videoIds);

// أو استخراج من Brightcove API calls في DevTools > Network
// ابحث عن: edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}
```

أو يمكنك نسخ جميع network requests من DevTools > Network tab:
1. انقر بزر الماوس الأيمن على أي request
2. اختر "Save all as HAR with content"
3. احفظ الملف، ثم سأستخدمه لاستخراج جميع video IDs تلقائياً

""")

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

print(f"\n📊 الفيديوهات الموجودة حالياً: {len(existing_videos)}")
if existing_videos:
    print("الفيديوهات الموجودة:")
    for i, v in enumerate(existing_videos, 1):
        print(f"   {i}. {v['title']} - Yanfaa ID: {v['yanfaa_video_id']}, Brightcove: {v['brightcove_video_id']}")

print(f"\n🎯 الهدف: استخراج جميع video IDs من 29 درس")
print(f"📝 المتبقي: {29 - len(existing_videos)} فيديو\n")

# Video IDs المعروفة من Yanfaa API (نحتاج إلى استخراج الباقي من network requests)
known_video_ids = {
    1125: {"brightcove": "6253662723001", "title": "Promo - Learn English (Level 1)"},
    1136: {"brightcove": "6247287755001", "title": "11- descreptions"},
    1137: {"brightcove": "6247290379001", "title": "12- clothes -colors"},
    1138: {"brightcove": "6247288259001", "title": "13- wearing and not wearing"},
    1139: {"brightcove": "6247290382001", "title": "14- excerise wearing-"},
    1146: {"brightcove": "6247297128001", "title": "21- Transportation"},
    1149: {"brightcove": "6247292063001", "title": "24- Family-"}
}

# استخراج Brightcove IDs من الفيديوهات الموجودة
existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}

print("💡 نصيحة: عند النقر على كل درس، ابحث في Network tab عن:")
print("   - edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}")
print("   - أو manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/...")
print("\n⏳ بعد أن تنقر على جميع الدروس وتستخرج video IDs، أضفها أدناه...\n")

# حفظ القائمة الحالية
with open(existing_videos_file, 'w', encoding='utf-8') as f:
    json.dump(existing_videos, f, indent=2, ensure_ascii=False)

print(f"✅ تم حفظ {len(existing_videos)} فيديو في: {existing_videos_file}")



