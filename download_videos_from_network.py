"""
تحميل الفيديوهات باستخدام HLS URLs المستخرجة من network requests
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from urllib.parse import unquote

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 تحميل {len(videos)} فيديو من الكورس: {course_slug}\n")

# HLS URLs المستخرجة من network requests
# هذه URLs تحتوي على fastly_token الذي قد يكون مؤقتاً، لكن نبدأ بها
hls_urls = {
    1136: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/20a5f2e1-822b-4c07-ba10-f32608bb58af/10s/master.m3u8?fastly_token=NjkzMmIwNmNfMDYwMWYwMmZmOGZkMGZhNzM0MjA4OTJkMDVjNmI5ZDc1ZDY0YWUwYjU1NDM5OGJjZmUwMDk5MGQwYTU4MmQ5Yw%3D%3D",
    1137: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/ca342b83-0700-4fa3-a17d-7d3fa5d3b9e3/10s/master.m3u8?fastly_token=NjkzMmIxYmRfNjY5ZjZmZjQ1MzhlYjI3NmQ0MzM3OTQ1ZDg5MDljZWRkYjUyNGE5MTg5NmMyMTFjODZmZjc2MjQ1NWY1Y2VkZg%3D%3D",
    1138: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/5c8cb696-6f39-4ee5-99e3-330d97b1965b/10s/master.m3u8?fastly_token=NjkzMmIyMzFfMGM4NDE3YTVhYjk0MGYzNDA2ZjRlNTQ5YTQ2ZTIyNWU3OTFmNTNlODkzNmM4YTdmMGRlMDkzYmU1OWJhOWQxMQ%3D%3D",
    1139: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a0c7713c-f8c8-4d1d-b582-8ab98027dbb3/10s/master.m3u8?fastly_token=NjkzMmIwNWFfYTdiY2UzYTNiYmIzZWY2NGExZGZmMjY4YTEzZDcxYjkwMmM1NjgzNDJkYWYzZTM4MjcxNjE5ZjlkOTA1MmRjNw%3D%3D",
    1146: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/c08b0e39-7af8-4da0-9563-3182828845cf/10s/master.m3u8?fastly_token=NjkzMmIxZGVfMzNjMTk2NDQ0OGE1YjE2YTc2ZjdhM2QwYWUwYTEyOTgwOTNiZDFjOTA2Y2NlNzQwYWUwMWE2NmVhZTQwNTBiOQ%3D%3D",
    1149: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a10d4e32-dc35-4629-9898-aee424720d0c/10s/master.m3u8?fastly_token=NjkzMmIwYzhfNTAzODIzMzk2ZjQwNTMwNTViY2EzYjJhMTEzOGU4M2IzZjJlZDg5Y2ZmOGIyNjVjMDBjZmZkN2NlYzg4MTBlNQ%3D%3D"
}

# قراءة cookies
cookies_file = Path('cookies_yanfaa_account.json')
cookies_dict = {}

if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    for name, data in cookies_data.items():
        if isinstance(data, dict):
            cookies_dict[name] = data.get('value', '')
        else:
            cookies_dict[name] = str(data)
    
    print(f"✅ تم تحميل {len(cookies_dict)} cookies\n")

downloaded = []
errors = []

for i, video in enumerate(videos, 1):
    yanfaa_video_id = video['yanfaa_video_id']
    brightcove_id = video['brightcove_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 {title}")
    print(f"   Yanfaa ID: {yanfaa_video_id}, Brightcove: {brightcove_id}")
    
    # الحصول على HLS URL
    hls_url = hls_urls.get(yanfaa_video_id)
    
    if not hls_url:
        errors.append(f"{title}: لم يتم العثور على HLS URL في network requests")
        print(f"   ❌ لم يتم العثور على HLS URL\n")
        continue
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    output_file = output_dir / f"{safe_title}.mp4"
    
    print(f"   📥 تحميل من HLS URL...")
    print(f"   URL: {hls_url[:80]}...")
    
    try:
        # تحميل باستخدام ffmpeg مع cookies
        # إنشاء ملف cookies Netscape لـ ffmpeg
        netscape_cookies_file = output_dir / "ffmpeg_cookies.txt"
        with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n\n")
            
            for name, value in cookies_dict.items():
                f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
        
        # فك تشفير fastly_token في URL
        hls_url_decoded = unquote(hls_url)
        
        # تحميل باستخدام ffmpeg
        ffmpeg_cmd = [
            'ffmpeg',
            '-headers', f'Referer: https://yanfaa.com/us/single/{course_slug}',
            '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-cookies', str(netscape_cookies_file),
            '-i', hls_url_decoded,
            '-c', 'copy',  # نسخ بدون re-encoding
            '-bsf:a', 'aac_adtstoasc',  # تصحيح BSF للaudio
            '-y',  # Overwrite
            str(output_file)
        ]
        
        print(f"   🔄 تشغيل ffmpeg...")
        process = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600
        )
        
        if process.returncode == 0 and output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            downloaded.append(f"{title} ({file_size:.2f} MB)")
            print(f"   ✅ تم التحميل بنجاح! ({file_size:.2f} MB)\n")
        else:
            error_msg = process.stderr[-300:] if process.stderr else "Unknown error"
            errors.append(f"{title}: {error_msg}")
            print(f"   ❌ فشل التحميل: {error_msg[:150]}\n")
    
    except FileNotFoundError:
        errors.append(f"{title}: ffmpeg غير مثبت")
        print(f"   ❌ ffmpeg غير مثبت. يرجى تثبيته من https://ffmpeg.org/\n")
    
    except subprocess.TimeoutExpired:
        errors.append(f"{title}: Timeout")
        print(f"   ⏱️ تجاوز الوقت المحدد\n")
    
    except Exception as e:
        errors.append(f"{title}: {str(e)}")
        print(f"   ❌ خطأ: {str(e)}\n")

# عرض النتائج
print("="*60)
print(f"📊 النتائج:")
print(f"✅ تم تحميل: {len(downloaded)} فيديو")
print(f"❌ فشل: {len(errors)} فيديو")

if downloaded:
    print("\n✅ الفيديوهات المحمّلة:")
    for item in downloaded:
        print(f"   - {item}")

if errors:
    print("\n❌ الأخطاء:")
    for error in errors:
        print(f"   - {error}")

print("\n" + "="*60)



