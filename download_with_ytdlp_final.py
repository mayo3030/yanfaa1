"""
تحميل الفيديوهات باستخدام yt-dlp مع Brightcove video IDs
yt-dlp أفضل في التعامل مع Brightcove DRM ويختار جودة مناسبة تلقائياً
"""
import json
import subprocess
import sys
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 تحميل {len(videos)} فيديو من الكورس: {course_slug}\n")

# قراءة cookies وتحويلها إلى Netscape format
cookies_file = Path('cookies_yanfaa_account.json')
netscape_cookies_file = output_dir / "cookies.txt"

if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    # إنشاء ملف Netscape cookies
    with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
        f.write("# This is a generated file! Do not edit.\n\n")
        
        for name, data in cookies_data.items():
            if isinstance(data, dict):
                domain = data.get('domain', '.yanfaa.com')
                path = data.get('path', '/')
                secure = 'TRUE' if data.get('secure', False) else 'FALSE'
                expiry = str(int(data.get('expiration', data.get('expires', 0))))
                value = data.get('value', '')
            else:
                domain = '.yanfaa.com'
                path = '/'
                secure = 'FALSE'
                expiry = '0'
                value = str(data)
            
            # Netscape format
            flag = 'TRUE' if domain.startswith('.') else 'FALSE'
            if not domain.startswith('.'):
                domain = '.' + domain
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
    
    print(f"✅ تم إنشاء ملف cookies: {netscape_cookies_file}\n")
else:
    print("⚠️ لم يتم العثور على ملف cookies\n")

downloaded = []
errors = []

for i, video in enumerate(videos, 1):
    brightcove_id = video['brightcove_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 {title}")
    print(f"   Brightcove ID: {brightcove_id}")
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    filename_template = str(output_dir / f"{safe_title}.%(ext)s")
    
    # Brightcove player URL
    video_url = f"https://players.brightcove.net/6164421959001/default_default/index.html?videoId={brightcove_id}"
    
    # yt-dlp command مع تحديد جودة متوسطة لتقليل الحجم
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--cookies', str(netscape_cookies_file),
        '--referer', f'https://yanfaa.com/us/single/{course_slug}',
        '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]',  # جودة 720p كحد أقصى
        '--merge-output-format', 'mp4',
        '-o', filename_template,
        '--no-warnings',
        '--console-title',
        video_url
    ]
    
    try:
        print(f"   📥 تحميل باستخدام yt-dlp (جودة 720p)...")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600  # 10 دقائق لكل فيديو
        )
        
        # البحث عن الملف المحمّل
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
            errors.append(f"{title}: {error_msg}")
            print(f"   ❌ فشل التحميل: {error_msg[:200]}\n")
    
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



