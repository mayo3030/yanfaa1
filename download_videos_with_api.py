"""
تحميل الفيديوهات باستخدام Brightcove API مباشرة و ffmpeg
"""
import json
import subprocess
import sys
import re
import httpx
from pathlib import Path

course_slug = 'learning_english_level_one'
session_id = 'bLfuY7nKLqWkFDeaZ4HuBlDukhiT8YRMbr36Tv8r'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 تحميل {len(videos)} فيديو من الكورس: {course_slug}\n")

# قراءة cookies
cookies_file = Path('cookies_yanfaa_account.json')
cookies_dict = {}

if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    # تحويل cookies إلى dict لاستخدامها مع httpx
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
    brightcove_id = video['brightcove_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 تحميل: {title}")
    print(f"   Brightcove ID: {brightcove_id}")
    
    # تنظيف العنوان ليستخدم كاسم ملف
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    output_file = output_dir / f"{safe_title}.mp4"
    
    try:
        # 1. الحصول على معلومات الفيديو من Brightcove API
        bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{brightcove_id}"
        bc_headers = {
            'Accept': 'application/json;pk=BCpkADawqM2QRYsRmY6RjR7_kxpL-RYC2FvGh4I5WRvwYiUHfYjjQNxNB6CpjKILFBLnHRW7hD8bMV7kDG4bTcSejh0LlIf1MCEHzV4NZ9_9L4xLp1FvU1sD0dxJaXnLLqxNHh5H',
            'Origin': 'https://yanfaa.com',
            'Referer': f'https://yanfaa.com/us/single/{course_slug}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # استخدام httpx مع cookies
        client = httpx.Client(cookies=cookies_dict, headers=bc_headers, timeout=30)
        response = client.get(bc_url)
        response.raise_for_status()
        video_data = response.json()
        
        # البحث عن HLS source
        sources = video_data.get('sources', [])
        hls_url = None
        
        for source in sources:
            src = source.get('src', '')
            src_type = source.get('type', '')
            
            # البحث عن HLS manifest
            if 'm3u8' in src or 'application/x-mpegURL' in src_type or 'application/vnd.apple.mpegurl' in src_type:
                hls_url = src
                break
        
        if not hls_url:
            # إذا لم نجد HLS، نبحث في أي source يحتوي على .m3u8
            for source in sources:
                src = source.get('src', '')
                if '.m3u8' in src:
                    hls_url = src
                    break
        
        if not hls_url:
            errors.append(f"{title}: لم يتم العثور على HLS URL")
            print(f"   ❌ لم يتم العثور على HLS URL في مصادر الفيديو\n")
            continue
        
        print(f"   ✅ تم العثور على HLS URL")
        print(f"   📥 التحميل باستخدام ffmpeg...")
        
        # 2. تحميل باستخدام ffmpeg مع cookies
        # إنشاء ملف cookies Netscape لـ ffmpeg
        netscape_cookies_file = output_dir / "ffmpeg_cookies.txt"
        with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n\n")
            
            for name, value in cookies_dict.items():
                f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
        
        # تحميل باستخدام ffmpeg
        ffmpeg_cmd = [
            'ffmpeg',
            '-headers', f'Referer: https://yanfaa.com/us/single/{course_slug}',
            '-user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-i', hls_url,
            '-c', 'copy',  # نسخ بدون re-encoding (أسرع)
            '-bsf:a', 'aac_adtstoasc',  # تصحيح BSF للأudio
            '-y',  # Overwrite output file
            str(output_file)
        ]
        
        try:
            process = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600
            )
            
            if process.returncode == 0 and output_file.exists():
                downloaded.append(f"{title} (✅ تم)")
                file_size = output_file.stat().st_size / (1024 * 1024)  # MB
                print(f"   ✅ تم التحميل بنجاح: {title} ({file_size:.2f} MB)\n")
            else:
                error_msg = process.stderr or process.stdout
                errors.append(f"{title}: {error_msg[:200]}")
                print(f"   ❌ فشل التحميل: {error_msg[:200]}\n")
        
        except FileNotFoundError:
            errors.append(f"{title}: ffmpeg غير مثبت. يرجى تثبيت ffmpeg")
            print(f"   ❌ ffmpeg غير مثبت. يرجى تثبيت ffmpeg من https://ffmpeg.org/\n")
        
        except subprocess.TimeoutExpired:
            errors.append(f"{title}: Timeout (تجاوز الوقت المحدد)")
            print(f"   ⏱️ تجاوز الوقت المحدد: {title}\n")
        
        except Exception as e:
            errors.append(f"{title}: {str(e)}")
            print(f"   ❌ خطأ: {str(e)}\n")
        
        client.close()
    
    except httpx.HTTPStatusError as e:
        errors.append(f"{title}: HTTP {e.response.status_code} - {e.response.text[:200]}")
        print(f"   ❌ خطأ HTTP: {e.response.status_code}\n")
    
    except Exception as e:
        errors.append(f"{title}: {str(e)}")
        print(f"   ❌ خطأ: {str(e)}\n")

# عرض النتائج
print("\n" + "="*60)
print(f"📊 النتائج:")
print(f"✅ تم تحميل: {len(downloaded)} فيديو")
print(f"❌ فشل: {len(errors)} فيديو")

if downloaded:
    print("\n✅ الفيديوهات المحمّلة:")
    for item in downloaded:
        print(f"   - {item}")

if errors:
    print("\n❌ الأخطاء:")
    for error in errors[:10]:  # عرض أول 10 أخطاء فقط
        print(f"   - {error}")

print("\n" + "="*60)



