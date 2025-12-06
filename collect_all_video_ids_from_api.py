"""
جمع جميع video IDs تلقائياً من Yanfaa API
باستخدام video IDs المعروفة واستخراج الباقي من API
"""
import json
import re
import httpx
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة cookies
cookies_file = Path('cookies_yanfaa_account.json')
cookies_dict = {}
session_id = None

if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    for name, data in cookies_data.items():
        if isinstance(data, dict):
            value = data.get('value', '')
            cookies_dict[name] = value
            if name == 'session_id':
                session_id = value
        else:
            cookies_dict[name] = str(data)

# استخراج session_id من cookies إذا لم يكن موجوداً مباشرة
if not session_id:
    # البحث عن session_id في cookies
    for name, value in cookies_dict.items():
        if 'session' in name.lower():
            session_id = value
            break

# إذا لم نجد session_id، نحاول استخراجه من آخر network request
if not session_id:
    # من آخر network request رأيناه
    session_id = 'FStOWnBKN7ME4PBCPR7Uk6RxGCPNqDcYwPYrVfl9'

print(f"🔑 Session ID: {session_id}\n")

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Video IDs المعروفة من network requests وملف extracted_video_ids.json
known_videos = [
    # من network requests
    {"yanfaa_id": 1127, "brightcove_id": "6247275935001", "title": "02 - alphabet"},
    {"yanfaa_id": 1136, "brightcove_id": "6247287755001", "title": "11- descreptions"},
    {"yanfaa_id": 1137, "brightcove_id": "6247290379001", "title": "12- clothes -colors"},
    {"yanfaa_id": 1138, "brightcove_id": "6247288259001", "title": "13- wearing and not wearing"},
    {"yanfaa_id": 1139, "brightcove_id": "6247290382001", "title": "14- excerise wearing-"},
    {"yanfaa_id": 1146, "brightcove_id": "6247297128001", "title": "21- Transportation"},
    {"yanfaa_id": 1149, "brightcove_id": "6247292063001", "title": "24- Family-"},
]

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []
existing_yanfaa_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)
        existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")

# دمج القائمة المعروفة مع الموجودة
all_videos_dict = {v['yanfaa_video_id']: v for v in existing_videos}

for video in known_videos:
    if video['yanfaa_id'] not in all_videos_dict:
        all_videos_dict[video['yanfaa_id']] = {
            'yanfaa_video_id': video['yanfaa_id'],
            'brightcove_video_id': video['brightcove_id'],
            'title': video['title']
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
    except Exception:
        pass
    
    return None

# مسح video IDs من 1100 إلى 1200 (نطاق معقول)
print("\n🔍 بدء مسح video IDs من 1100 إلى 1200...\n")

ids_to_check = [vid for vid in range(1100, 1201) if vid not in all_videos_dict]
print(f"📋 سيتم فحص {len(ids_to_check)} video IDs...\n")

found_videos = []

# فحص متوازي
max_workers = 10
completed = 0

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_id = {executor.submit(fetch_video_info, vid_id): vid_id for vid_id in ids_to_check}
    
    for future in as_completed(future_to_id):
        completed += 1
        video_id = future_to_id[future]
        
        try:
            result = future.result()
            if result:
                found_videos.append(result)
                all_videos_dict[result['yanfaa_video_id']] = result
                print(f"✅ [{completed}/{len(ids_to_check)}] وجد: {result['title']} (ID: {result['yanfaa_video_id']}, Brightcove: {result['brightcove_video_id']})")
            elif completed % 50 == 0:
                print(f"⏳ [{completed}/{len(ids_to_check)}] فحص {video_id}...")
        except Exception:
            pass

# تحويل إلى list وترتيب
all_videos = sorted(all_videos_dict.values(), key=lambda x: x['yanfaa_video_id'])

print(f"\n📊 النتائج:")
print(f"✅ وجد {len(found_videos)} فيديو جديد")
print(f"📦 الإجمالي: {len(all_videos)} فيديو")

# حفظ النتائج
output_file = output_dir / "extracted_video_ids.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_videos, f, indent=2, ensure_ascii=False)

print(f"\n💾 تم حفظ جميع video IDs في: {output_file}")

# عرض القائمة
print("\n📋 قائمة جميع الفيديوهات:")
for i, video in enumerate(all_videos, 1):
    print(f"   {i:2d}. {video['title']} - Yanfaa ID: {video['yanfaa_video_id']}, Brightcove: {video['brightcove_video_id']}")

print(f"\n🎯 الهدف: 29 فيديو | الموجود: {len(all_videos)} فيديو")

if len(all_videos) < 29:
    print(f"⚠️ لا تزال توجد {29 - len(all_videos)} فيديو مفقود")
    print("💡 قد تحتاج إلى:")
    print("   1. توسيع نطاق البحث (مثلاً من 1000 إلى 1300)")
    print("   2. استخدام browser automation للنقر على جميع الدروس")
else:
    print("✅ تم العثور على جميع الفيديوهات!")



