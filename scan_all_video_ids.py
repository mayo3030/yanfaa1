"""
مسح جميع video IDs المحتملة للكورس
"""
import httpx
import json
from pathlib import Path
import time
from proxy_helper import get_httpx_client

session_id = 'bLfuY7nKLqWkFDeaZ4HuBlDukhiT8YRMbr36Tv8r'
course_slug = 'learning_english_level_one'

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# Video IDs المعروفة بالفعل
known_video_ids = [1136, 1137, 1138, 1139, 1146, 1149]

print(f"📚 مسح video IDs للكورس: {course_slug}")
print(f"🔑 Session ID: {session_id}\n")

found_videos = []

# مسح نطاق من video IDs
# من الملاحظ أن video IDs تبدأ من حوالي 1136
start_id = 1100
end_id = 1200

print(f"🔍 مسح video IDs من {start_id} إلى {end_id}...\n")

for video_id in range(start_id, end_id + 1):
    # تخطي المعروفة بالفعل
    if video_id in known_video_ids:
        continue
    
    video_url = f'https://app.yanfaa.com/api/videos/{video_id}?session_id={session_id}'
    try:
        with get_httpx_client(headers=headers, timeout=3) as client:
            r = client.get(video_url)
        if r.status_code == 200:
            video_data = r.json()
            brightcove_id = video_data.get('brightcove_video_id') or video_data.get('video_id')
            title = video_data.get('title', f'Video {video_id}')
            
            if brightcove_id:
                video_info = {
                    "yanfaa_video_id": video_id,
                    "brightcove_video_id": brightcove_id,
                    "title": title
                }
                found_videos.append(video_info)
                print(f"✅ [{video_id}] {title} - Brightcove: {brightcove_id}")
        
        # تأخير بسيط لتجنب rate limiting
        time.sleep(0.1)
        
    except httpx.HTTPStatusError:
        pass  # 404 أو أخطاء أخرى - متوقع
    except Exception as e:
        print(f"⚠️ خطأ في video ID {video_id}: {str(e)}")

# حفظ جميع الفيديوهات
all_videos_file = output_dir / "all_scanned_video_ids.json"
with open(all_videos_file, 'w', encoding='utf-8') as f:
    json.dump(found_videos, f, indent=2, ensure_ascii=False)

print(f"\n📹 تم العثور على {len(found_videos)} فيديو إضافي")
print(f"✅ تم الحفظ إلى {all_videos_file}")

