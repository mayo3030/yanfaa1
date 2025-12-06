"""
تحميل الفيديوهات مباشرة من HLS URLs المحفوظة (من network requests)
بدون الحاجة إلى API calls
"""
import json
import subprocess
import sys
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# HLS URLs من network requests (قد تحتاج إلى تحديث)
hls_urls_map = {
    1136: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/20a5f2e1-822b-4c07-ba10-f32608bb58af/10s/master.m3u8?fastly_token=NjkzMmIwNmNfMDYwMWYwMmZmOGZkMGZhNzM0MjA4OTJkMDVjNmI5ZDc1ZDY0YWUwYjU1NDM5OGJjZmUwMDk5MGQwYTU4MmQ5Yw%3D%3D",
    1137: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/ca342b83-0700-4fa3-a17d-7d3fa5d3b9e3/10s/master.m3u8?fastly_token=NjkzMmIxYmRfNjY5ZjZmZjQ1MzhlYjI3NmQ0MzM3OTQ1ZDg5MDljZWRkYjUyNGE5MTg5NmMyMTFjODZmZjc2MjQ1NWY1Y2VkZg%3D%3D",
    1138: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/5c8cb696-6f39-4ee5-99e3-330d97b1965b/10s/master.m3u8?fastly_token=NjkzMmIyMzFfMGM4NDE3YTVhYjk0MGYzNDA2ZjRlNTQ5YTQ2ZTIyNWU3OTFmNTNlODkzNmM4YTdmMGRlMDkzYmU1OWJhOWQxMQ%3D%3D",
    1139: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a0c7713c-f8c8-4d1d-b582-8ab98027dbb3/10s/master.m3u8?fastly_token=NjkzMmIwNWFfYTdiY2UzYTNiYmIzZWY2NGExZGZmMjY4YTEzZDcxYjkwMmM1NjgzNDJkYWYzZTM4MjcxNjE5ZjlkOTA1MmRjNw%3D%3D",
    1146: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/c08b0e39-7af8-4da0-9563-3182828845cf/10s/master.m3u8?fastly_token=NjkzMmIxZGVfMzNjMTk2NDQ0OGE1YjE2YTc2ZjdhM2QwYWUwYTEyOTgwOTNiZDFjOTA2Y2NlNzQwYWUwMWE2NmVhZTQwNTBiOQ%3D%3D",
    1149: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a10d4e32-dc35-4629-9898-aee424720d0c/10s/master.m3u8?fastly_token=NjkzMmIwYzhfNTAzODIzMzk2ZjQwNTMwNTViY2EzYjJhMTEzOGU4M2IzZjJlZDg5Y2ZmOGIyNjVjMDBjZmZkN2NlYzg4MTBlNQ%3D%3D"
}

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 تحميل {len(videos)} فيديو مباشرة من HLS URLs\n")

# قراءة cookies لإنشاء Netscape cookies file
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

# إنشاء Netscape cookies file
netscape_cookies_file = output_dir / "cookies.txt"
with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
    f.write("# Netscape HTTP Cookie File\n\n")
    for name, value in cookies_dict.items():
        f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")

downloaded = []
errors = []
redownload = []  # فيديوهات لإعادة التحميل بجودة أقل

for i, video in enumerate(videos, 1):
    yanfaa_video_id = video['yanfaa_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 {title}")
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    
    # البحث عن HLS URL
    hls_url = hls_urls_map.get(yanfaa_video_id)
    
    if not hls_url:
        errors.append(f"{title}: لا يوجد HLS URL محفوظ")
        print(f"   ❌ لا يوجد HLS URL محفوظ لهذا الفيديو\n")
        continue
    
    # فحص الملف الحالي
    output_file = output_dir / f"{safe_title}.mp4"
    file_exists = False
    file_size_mb = 0
    
    # البحث عن ملف بأي extension
    for ext in ['mp4', 'mkv', 'webm']:
        potential_file = output_dir / f"{safe_title}.{ext}"
        if potential_file.exists():
            output_file = potential_file
            file_exists = True
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            break
    
    # إذا كان الملف موجوداً وأصغر من 100 ميجابايت، تخطي
    if file_exists and file_size_mb < 100:
        print(f"   ⏭️ الملف موجود ({file_size_mb:.2f} MB) - تخطي\n")
        downloaded.append(f"{title} ({file_size_mb:.2f} MB)")
        continue
    
    # إذا كان الملف كبيراً (أكثر من 100 MB)، نعيد تحميله بجودة أقل
    if file_exists and file_size_mb > 100:
        print(f"   ⚠️ الملف كبير جداً ({file_size_mb:.2f} MB) - إعادة تحميل بجودة 480p")
        output_file.unlink()  # حذف الملف القديم
        redownload.append(title)
    
    try:
        print(f"   📥 تحميل من HLS URL (جودة 480p)...")
        
        # استخدام yt-dlp لتحميل HLS مباشرة بجودة 480p
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--cookies', str(netscape_cookies_file),
            '--referer', f'https://yanfaa.com/us/single/{course_slug}',
            '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',  # جودة 480p
            '--merge-output-format', 'mp4',
            '--no-warnings',
            '--no-playlist',
            '-o', str(output_file).replace('.mp4', '.%(ext)s'),
            hls_url
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600
        )
        
        # التحقق من وجود الملف المحمّل
        downloaded_file = None
        for ext in ['mp4', 'mkv', 'webm']:
            potential_file = output_dir / f"{safe_title}.{ext}"
            if potential_file.exists():
                downloaded_file = potential_file
                break
        
        if downloaded_file and downloaded_file.exists():
            file_size = downloaded_file.stat().st_size / (1024 * 1024)  # MB
            downloaded.append(f"{title} ({file_size:.2f} MB)")
            print(f"   ✅ تم التحميل بنجاح! ({file_size:.2f} MB)\n")
        else:
            error_msg = process.stderr[-300:] if process.stderr else process.stdout[-300:]
            if not error_msg:
                error_msg = "لم يتم إنشاء ملف بعد التحميل"
            errors.append(f"{title}: {error_msg[:150]}")
            print(f"   ❌ فشل: {error_msg[:150]}\n")
    
    except subprocess.TimeoutExpired:
        errors.append(f"{title}: timeout بعد 10 دقائق")
        print(f"   ❌ timeout\n")
    except Exception as e:
        errors.append(f"{title}: {str(e)}")
        print(f"   ❌ خطأ: {str(e)}\n")

# عرض النتائج
print("="*60)
print(f"📊 النتائج:")
print(f"✅ تم تحميل/إعادة تحميل: {len(downloaded)} فيديو")
print(f"❌ فشل: {len(errors)} فيديو")

if downloaded:
    print("\n✅ الفيديوهات المحمّلة:")
    for item in downloaded:
        print(f"   - {item}")

if redownload:
    print(f"\n🔄 تم إعادة تحميل {len(redownload)} فيديو بجودة أقل:")
    for title in redownload:
        print(f"   - {title}")

if errors:
    print("\n❌ الأخطاء:")
    for error in errors:
        print(f"   - {error}")

print("\n" + "="*60)



