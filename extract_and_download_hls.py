"""
استخراج HLS URLs من network requests مباشرة وتحميلها
"""
import json
import subprocess
import sys
import re
from pathlib import Path
import httpx

course_slug = 'learning_english_level_one'
session_id = 'bLfuY7nKLqWkFDeaZ4HuBlDukhiT8YRMbr36Tv8r'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 تحميل {len(videos)} فيديو\n")

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

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

downloaded = []
errors = []

for i, video in enumerate(videos, 1):
    yanfaa_video_id = video['yanfaa_video_id']
    brightcove_id = video['brightcove_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 {title}")
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    output_file = output_dir / f"{safe_title}.mp4"
    
    # إذا كان الملف موجوداً، تخطي
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:  # إذا كان أكبر من 10 ميجابايت
            print(f"   ⏭️ الملف موجود ({file_size_mb:.2f} MB) - تخطي\n")
            downloaded.append(f"{title} ({file_size_mb:.2f} MB)")
            continue
    
    try:
        # 1. الحصول على معلومات الفيديو من Yanfaa API
        yanfaa_url = f'https://app.yanfaa.com/api/videos/{yanfaa_video_id}?session_id={session_id}'
        
        client = httpx.Client(cookies=cookies_dict, headers=headers, timeout=30)
        response = client.get(yanfaa_url)
        
        if response.status_code != 200:
            errors.append(f"{title}: Yanfaa API {response.status_code}")
            print(f"   ❌ خطأ في Yanfaa API: {response.status_code}\n")
            client.close()
            continue
        
        video_info = response.json()
        print(f"   ✅ تم الحصول على معلومات الفيديو")
        
        # 2. محاولة الحصول على HLS URL من Brightcove API
        # Brightcove قد يحتاج policy key صحيح، لكن نحاول بدون policy key أولاً
        bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{brightcove_id}"
        bc_response = client.get(bc_url, headers={
            'Accept': 'application/json',
            'Origin': 'https://yanfaa.com',
            'Referer': f'https://yanfaa.com/us/single/{course_slug}',
        })
        
        hls_url = None
        
        if bc_response.status_code == 200:
            bc_data = bc_response.json()
            sources = bc_data.get('sources', [])
            
            # البحث عن HLS source
            for source in sources:
                src = source.get('src', '')
                src_type = source.get('type', '')
                
                if '.m3u8' in src or 'application/x-mpegURL' in src_type or 'application/vnd.apple.mpegurl' in src_type:
                    hls_url = src
                    break
        
        client.close()
        
        if not hls_url:
            # إذا لم نجد HLS URL، نستخدم HLS URLs المستخرجة من network requests
            hls_urls_from_network = {
                1136: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/20a5f2e1-822b-4c07-ba10-f32608bb58af/10s/master.m3u8?fastly_token=NjkzMmIwNmNfMDYwMWYwMmZmOGZkMGZhNzM0MjA4OTJkMDVjNmI5ZDc1ZDY0YWUwYjU1NDM5OGJjZmUwMDk5MGQwYTU4MmQ5Yw%3D%3D",
                1137: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/ca342b83-0700-4fa3-a17d-7d3fa5d3b9e3/10s/master.m3u8?fastly_token=NjkzMmIxYmRfNjY5ZjZmZjQ1MzhlYjI3NmQ0MzM3OTQ1ZDg5MDljZWRkYjUyNGE5MTg5NmMyMTFjODZmZjc2MjQ1NWY1Y2VkZg%3D%3D",
                1138: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/5c8cb696-6f39-4ee5-99e3-330d97b1965b/10s/master.m3u8?fastly_token=NjkzMmIyMzFfMGM4NDE3YTVhYjk0MGYzNDA2ZjRlNTQ5YTQ2ZTIyNWU3OTFmNTNlODkzNmM4YTdmMGRlMDkzYmU1OWJhOWQxMQ%3D%3D",
                1139: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a0c7713c-f8c8-4d1d-b582-8ab98027dbb3/10s/master.m3u8?fastly_token=NjkzMmIwNWFfYTdiY2UzYTNiYmIzZWY2NGExZGZmMjY4YTEzZDcxYjkwMmM1NjgzNDJkYWYzZTM4MjcxNjE5ZjlkOTA1MmRjNw%3D%3D",
                1146: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/c08b0e39-7af8-4da0-9563-3182828845cf/10s/master.m3u8?fastly_token=NjkzMmIxZGVfMzNjMTk2NDQ0OGE1YjE2YTc2ZjdhM2QwYWUwYTEyOTgwOTNiZDFjOTA2Y2NlNzQwYWUwMWE2NmVhZTQwNTBiOQ%3D%3D",
                1149: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a10d4e32-dc35-4629-9898-aee424720d0c/10s/master.m3u8?fastly_token=NjkzMmIwYzhfNTAzODIzMzk2ZjQwNTMwNTViY2EzYjJhMTEzOGU4M2IzZjJlZDg5Y2ZmOGIyNjVjMDBjZmZkN2NlYzg4MTBlNQ%3D%3D"
            }
            hls_url = hls_urls_from_network.get(yanfaa_video_id)
        
        if not hls_url:
            errors.append(f"{title}: لم يتم العثور على HLS URL")
            print(f"   ❌ لم يتم العثور على HLS URL\n")
            continue
        
        print(f"   📥 تحميل من HLS URL...")
        
        # استخدام yt-dlp لتحميل HLS مباشرة (أفضل من ffmpeg)
        netscape_cookies_file = output_dir / "cookies.txt"
        if not netscape_cookies_file.exists():
            with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n\n")
                for name, value in cookies_dict.items():
                    f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
        
        # yt-dlp مع HLS URL مباشرة وتحديد جودة 480p لتقليل الحجم
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--cookies', str(netscape_cookies_file),
            '--referer', f'https://yanfaa.com/us/single/{course_slug}',
            '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',  # جودة 480p كحد أقصى
            '--merge-output-format', 'mp4',
            '-o', str(output_file).replace('.mp4', '.%(ext)s'),
            '--no-warnings',
            hls_url
        ]
        
        print(f"   🔄 تشغيل yt-dlp (جودة 480p لتقليل الحجم)...")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600
        )
        
        # التحقق من وجود الملف المحمّل
        downloaded_file = output_file
        if not downloaded_file.exists():
            for ext in ['mp4', 'mkv', 'webm']:
                potential_file = output_dir / f"{safe_title}.{ext}"
                if potential_file.exists():
                    downloaded_file = potential_file
                    break
        
        if downloaded_file.exists():
            file_size = downloaded_file.stat().st_size / (1024 * 1024)  # MB
            downloaded.append(f"{title} ({file_size:.2f} MB)")
            print(f"   ✅ تم التحميل بنجاح! ({file_size:.2f} MB)\n")
        else:
            error_msg = process.stderr[-200:] if process.stderr else process.stdout[-200:]
            errors.append(f"{title}: {error_msg}")
            print(f"   ❌ فشل: {error_msg[:150]}\n")
    
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

print("\n" + "="*60)



