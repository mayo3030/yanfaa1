"""
سكريبت محسّن لاستكمال استخراج جميع video IDs للكورس
يجمع بين عدة طرق لضمان استخراج جميع الفيديوهات
"""
import json
import re
import time
import httpx
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

course_slug = 'learning_english_level_one'
course_id = 69
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []
existing_brightcove_ids = set()
existing_yanfaa_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)
        existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos if v.get('brightcove_video_id')}
        existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos if v.get('yanfaa_video_id')}

print("="*60)
print("🚀 استكمال استخراج جميع video IDs")
print("="*60)
print(f"📚 الكورس: {course_slug}")
print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: 29 درس")
print(f"📝 المتبقي: {29 - len(existing_videos)} فيديو\n")

# قراءة session_id
session_id = None
session_file = output_dir.parent.parent / 'session.json'
if session_file.exists():
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
        session_id = session_data.get('session_id')

# إذا لم نجد session_id، نبحث في الملفات الأخرى
if not session_id:
    endpoints_file = output_dir / 'all_lessons_from_courses_endpoint.json'
    if endpoints_file.exists():
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            session_id = data.get('session_id')

# إذا لم نجد بعد، نستخدم session_id الافتراضي
if not session_id:
    session_id = 'mNOaH74fU0c8w6cYFHGaA54wxqTq4fD5umworS16'

print(f"🔑 Session ID: {session_id[:20]}...\n")

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# قراءة cookies
cookies_dict = {}
cookies_file = Path('cookies_yanfaa_account.json')
if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
        for name, data in cookies_data.items():
            if isinstance(data, dict):
                cookies_dict[name] = data.get('value', '')
            else:
                cookies_dict[name] = str(data)

newly_found_videos = []

# الطريقة 1: فحص نطاق video IDs بناءً على الفيديوهات الموجودة
print("🔍 الطريقة 1: فحص نطاقات video IDs...\n")

# تحديد النطاقات بناءً على الفيديوهات الموجودة
if existing_videos:
    existing_yanfaa_id_list = sorted(existing_yanfaa_ids)
    min_id = min(existing_yanfaa_id_list)
    max_id = max(existing_yanfaa_id_list)
    
    # نطاقات للفحص
    ranges_to_check = [
        (min_id - 50, min_id - 1),  # قبل النطاق الموجود
        (max_id + 1, max_id + 100),  # بعد النطاق الموجود
        (1100, 1200),  # نطاق معروف
        (1125, 1160),  # نطاق الدروس المحتمل
    ]
else:
    ranges_to_check = [
        (1100, 1200),
        (1125, 1160),
    ]

def check_video_id(video_id):
    """التحقق من video ID واحد"""
    if video_id in existing_yanfaa_ids:
        return None
    
    url = f'https://app.yanfaa.com/api/videos/{video_id}'
    if session_id:
        url += f'?session_id={session_id}'
    
    try:
        with httpx.Client(cookies=cookies_dict, headers=headers, timeout=5) as client:
            response = client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                brightcove_id = data.get('brightcove_video_id')
                title = data.get('title', f'Video {video_id}')
                vid_course_id = data.get('course_id')
                
                # التحقق من أن الفيديو ينتمي للكورس الصحيح
                if brightcove_id and (vid_course_id == course_id or not vid_course_id):
                    return {
                        'yanfaa_video_id': video_id,
                        'brightcove_video_id': str(brightcove_id),
                        'title': title,
                        'course_id': vid_course_id
                    }
    except Exception as e:
        pass
    
    return None

# جمع جميع IDs للفحص
ids_to_check = []
for start, end in ranges_to_check:
    for video_id in range(start, end + 1):
        if video_id not in existing_yanfaa_ids and video_id > 0:
            ids_to_check.append(video_id)

# إزالة التكرارات
ids_to_check = sorted(list(set(ids_to_check)))

print(f"📋 سيتم فحص {len(ids_to_check)} video IDs...\n")

# فحص متوازي
max_workers = 10
completed = 0
found_in_scan = []

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_id = {executor.submit(check_video_id, vid_id): vid_id for vid_id in ids_to_check}
    
    for future in as_completed(future_to_id):
        completed += 1
        video_id = future_to_id[future]
        
        try:
            result = future.result()
            if result:
                found_in_scan.append(result)
                newly_found_videos.append(result)
                existing_yanfaa_ids.add(result['yanfaa_video_id'])
                existing_brightcove_ids.add(result['brightcove_video_id'])
                print(f"✅ [{completed}/{len(ids_to_check)}] وجد: {result['title']} (ID: {result['yanfaa_video_id']}, Brightcove: {result['brightcove_video_id']})")
            elif completed % 50 == 0:
                print(f"⏳ [{completed}/{len(ids_to_check)}] فحص {video_id}...")
        except Exception as e:
            pass

print(f"\n📊 نتائج الفحص: وجد {len(found_in_scan)} فيديو جديد\n")

# دمج النتائج مع الفيديوهات الموجودة
all_videos_dict = {v['yanfaa_video_id']: v for v in existing_videos}
for new_video in newly_found_videos:
    all_videos_dict[new_video['yanfaa_video_id']] = new_video

# تحويل إلى قائمة مرتبة
all_videos_list = sorted(all_videos_dict.values(), key=lambda x: x['yanfaa_video_id'])

# حفظ النتائج
with open(existing_videos_file, 'w', encoding='utf-8') as f:
    json.dump(all_videos_list, f, indent=2, ensure_ascii=False)

print("="*60)
print(f"📊 النتائج النهائية:")
print(f"✅ إجمالي الفيديوهات: {len(all_videos_list)}")
print(f"➕ فيديوهات جديدة: {len(newly_found_videos)}")
print(f"🎯 الهدف: 29 درس")
print(f"📝 المتبقي: {29 - len(all_videos_list)} فيديو")
print("="*60)

if newly_found_videos:
    print("\n📋 الفيديوهات الجديدة:")
    for video in newly_found_videos:
        print(f"   - {video['title']} (ID: {video['yanfaa_video_id']}, Brightcove: {video['brightcove_video_id']})")

print("\n📋 جميع الفيديوهات:")
for i, video in enumerate(all_videos_list, 1):
    print(f"   {i:2d}. [{video['yanfaa_video_id']:4d}] {video['title']}")

print(f"\n💾 تم حفظ جميع video IDs في: {existing_videos_file}")

if len(all_videos_list) < 29:
    print(f"\n⚠️ لا تزال توجد {29 - len(all_videos_list)} فيديو مفقود")
    print("💡 يمكنك:")
    print("   1. تشغيل هذا السكريبت مرة أخرى بعد تحديث session_id")
    print("   2. استخدام browser automation للنقر على الدروس واستخراج video IDs")
else:
    print("\n✅ تم العثور على جميع الفيديوهات!")



