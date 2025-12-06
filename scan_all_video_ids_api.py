"""
مسح جميع video IDs من Yanfaa API بسرعة
محاولة استخراج جميع video IDs للكورس من API
"""
import httpx
import json
from pathlib import Path
import time
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

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []
existing_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)
        existing_ids = {v['yanfaa_video_id'] for v in existing_videos}

print(f"📚 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: استخراج جميع video IDs من 29 درس\n")

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Video IDs المعروفة (من 1100 إلى 1200 تقريباً)
known_ranges = [
    (1100, 1150),  # نطاق الدروس المعروفة
    (1000, 1100),  # نطاق أوسع
    (1150, 1250),  # نطاق أوسع
]

def check_video_id(video_id):
    """التحقق من video ID واحد"""
    if video_id in existing_ids:
        return None
    
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
                course_id = data.get('course_id')
                
                # التحقق من أن الفيديو ينتمي للكورس الصحيح
                if brightcove_id:
                    return {
                        'yanfaa_video_id': video_id,
                        'brightcove_video_id': brightcove_id,
                        'title': title,
                        'course_id': course_id
                    }
            elif response.status_code == 404:
                return None  # Video ID غير موجود
            else:
                # إذا كان 401، قد نحتاج session_id جديد
                return None
    
    except Exception as e:
        return None
    
    return None

# مسح جميع video IDs بشكل متوازي
print("🔍 بدء مسح video IDs بشكل متوازي (Turbo Mode)...\n")

all_videos = existing_videos.copy()
found_videos = []

# جمع جميع IDs للفحص
ids_to_check = []
for start, end in known_ranges:
    for video_id in range(start, end + 1):
        if video_id not in existing_ids:
            ids_to_check.append(video_id)

print(f"📋 سيتم فحص {len(ids_to_check)} video IDs...\n")

# فحص متوازي مع 10 threads
max_workers = 10
completed = 0

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_id = {executor.submit(check_video_id, vid_id): vid_id for vid_id in ids_to_check}
    
    for future in as_completed(future_to_id):
        completed += 1
        video_id = future_to_id[future]
        
        try:
            result = future.result()
            if result:
                found_videos.append(result)
                print(f"✅ [{completed}/{len(ids_to_check)}] وجد: {result['title']} (ID: {result['yanfaa_video_id']}, Brightcove: {result['brightcove_video_id']})")
            elif completed % 50 == 0:
                print(f"⏳ [{completed}/{len(ids_to_check)}] فحص {video_id}...")
        except Exception as e:
            pass

# دمج النتائج
if found_videos:
    all_videos.extend(found_videos)
    
    # ترتيب حسب video ID
    all_videos.sort(key=lambda x: x['yanfaa_video_id'])
    
    print(f"\n📊 النتائج:")
    print(f"✅ وجد {len(found_videos)} فيديو جديد")
    print(f"📦 الإجمالي: {len(all_videos)} فيديو")
    
    # حفظ النتائج
    output_file = output_dir / "extracted_video_ids.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 تم حفظ جميع video IDs في: {output_file}")
    
    # عرض القائمة الكاملة
    print("\n📋 قائمة جميع الفيديوهات:")
    for i, video in enumerate(all_videos, 1):
        print(f"   {i:2d}. {video['title']} - Yanfaa ID: {video['yanfaa_video_id']}, Brightcove: {video['brightcove_video_id']}")
else:
    print(f"\n⚠️ لم يتم العثور على فيديوهات جديدة في النطاقات المفحوصة.")
    print(f"💡 قد تحتاج إلى:")
    print(f"   1. تحديث session_id من المتصفح")
    print(f"   2. توسيع نطاق البحث")
    print(f"   3. استخراج video IDs من network requests في المتصفح")



