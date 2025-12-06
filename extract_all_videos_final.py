"""
استخراج جميع video IDs تلقائياً من network requests
وجمع جميع video IDs من جميع الدروس
"""
import json
import re
from pathlib import Path
import httpx

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

print("="*60)
print("🚀 استخراج جميع video IDs من 29 درس")
print("="*60)

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
all_videos = {}
existing_yanfaa_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing = json.load(f)
        for v in existing:
            all_videos[v['yanfaa_video_id']] = v
            existing_yanfaa_ids.add(v['yanfaa_video_id'])

# Video IDs المستخرجة من network requests
# من network requests المحفوظة:
found_from_network = [
    {"yanfaa_id": 1125, "brightcove_id": "6253662723001", "title": "Promo - learning englesh level one new promo", "type": "promo"},
    {"yanfaa_id": 1127, "brightcove_id": "6247275935001", "title": "02 - alphabet", "type": "lesson"},
    {"yanfaa_id": 1136, "brightcove_id": "6247287755001", "title": "11- descreptions", "type": "lesson"},
    {"yanfaa_id": 1137, "brightcove_id": "6247290379001", "title": "12- clothes -colors", "type": "lesson"},
    {"yanfaa_id": 1138, "brightcove_id": "6247288259001", "title": "13- wearing and not wearing", "type": "lesson"},
    {"yanfaa_id": 1139, "brightcove_id": "6247290382001", "title": "14- excerise wearing-", "type": "lesson"},
    {"yanfaa_id": 1146, "brightcove_id": "6247297128001", "title": "21- Transportation", "type": "lesson"},
    {"yanfaa_id": 1149, "brightcove_id": "6247292063001", "title": "24- Family-", "type": "lesson"},
]

# دمج مع الفيديوهات الموجودة
for video in found_from_network:
    if video['yanfaa_id'] not in all_videos:
        all_videos[video['yanfaa_id']] = {
            'yanfaa_video_id': video['yanfaa_id'],
            'brightcove_video_id': video['brightcove_id'],
            'title': video['title']
        }

print(f"\n📊 الفيديوهات الموجودة: {len(all_videos)}")
print(f"🎯 الهدف: 29 درس\n")

# قراءة cookies
cookies_file = Path('cookies_yanfaa_account.json')
cookies_dict = {}
session_id = 'FStOWnBKN7ME4PBCPR7Uk6RxGCPNqDcYwPYrVfl9'

if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
        for name, data in cookies_data.items():
            if isinstance(data, dict):
                cookies_dict[name] = data.get('value', '')
            else:
                cookies_dict[name] = str(data)

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_video_info(video_id):
    """جلب معلومات فيديو من API"""
    url = f'https://app.yanfaa.com/api/videos/{video_id}'
    if session_id:
        url += f'?session_id={session_id}'
    
    try:
        with httpx.Client(cookies=cookies_dict, headers=headers, timeout=5) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                brightcove_id = data.get('brightcove_video_id') or data.get('video_id')
                title = data.get('title', f'Video {video_id}')
                if brightcove_id:
                    return {
                        'yanfaa_video_id': video_id,
                        'brightcove_video_id': brightcove_id,
                        'title': title
                    }
    except:
        pass
    return None

# مسح نطاق أكبر للعثور على باقي video IDs
# من الملاحظات، video IDs تتراوح من 1125 إلى 1149
# قد تكون هناك video IDs بين 1125-1200
print("\n🔍 مسح video IDs من 1120 إلى 1160...\n")

ids_to_check = [vid for vid in range(1120, 1161) if vid not in all_videos]
print(f"📋 سيتم فحص {len(ids_to_check)} video IDs...\n")

found_new = 0
for video_id in ids_to_check:
    result = fetch_video_info(video_id)
    if result:
        all_videos[result['yanfaa_video_id']] = result
        found_new += 1
        print(f"✅ [{found_new}] وجد: {result['title']} (ID: {result['yanfaa_video_id']}, Brightcove: {result['brightcove_video_id']})")

# تحويل إلى list وترتيب
all_videos_list = sorted(all_videos.values(), key=lambda x: x['yanfaa_video_id'])

print(f"\n📊 النتائج:")
print(f"✅ إجمالي الفيديوهات: {len(all_videos_list)}")
print(f"🎯 الهدف: 29 درس\n")

# حفظ النتائج
output_file = output_dir / "extracted_video_ids.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_videos_list, f, indent=2, ensure_ascii=False)

print("📋 قائمة جميع الفيديوهات:")
for i, video in enumerate(all_videos_list, 1):
    print(f"   {i:2d}. {video['title']} - Yanfaa ID: {video['yanfaa_video_id']}, Brightcove: {video['brightcove_video_id']}")

print(f"\n💾 تم حفظ جميع video IDs في: {output_file}")

if len(all_videos_list) < 29:
    print(f"\n⚠️ لا تزال توجد {29 - len(all_videos_list)} فيديو مفقود")
    print("💡 سيتم استخدام browser automation للنقر على باقي الدروس...")
else:
    print("\n✅ تم العثور على جميع الفيديوهات!")



