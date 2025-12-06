"""
تحميل الفيديوهات باستخدام Yanfaa API ثم استخراج HLS URLs
"""
import json
import subprocess
import sys
import re
import httpx
from pathlib import Path
from proxy_helper import get_httpx_client

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
hls_urls_found = []

for i, video in enumerate(videos, 1):
    yanfaa_video_id = video['yanfaa_video_id']
    brightcove_id = video['brightcove_video_id']
    title = video['title']
    
    print(f"[{i}/{len(videos)}] 🎬 {title}")
    print(f"   Yanfaa ID: {yanfaa_video_id}, Brightcove: {brightcove_id}")
    
    try:
        # 1. الحصول على معلومات الفيديو من Yanfaa API
        yanfaa_url = f'https://app.yanfaa.com/api/videos/{yanfaa_video_id}?session_id={session_id}'
        
        client = get_httpx_client(cookies=cookies_dict, headers=headers, timeout=30)
        response = client.get(yanfaa_url)
        response.raise_for_status()
        video_info = response.json()
        
        print(f"   ✅ تم الحصول على معلومات الفيديو من Yanfaa API")
        
        # 2. محاولة الحصول على HLS URL من Brightcove API باستخدام policy key من المتصفح
        # من network requests، رأيت أن المتصفح يستخدم Brightcove API مباشرة
        # دعني أحاول استخدام نفس الطريقة
        
        bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{brightcove_id}"
        bc_headers = {
            'Accept': 'application/json',
            'Origin': 'https://yanfaa.com',
            'Referer': f'https://yanfaa.com/us/single/{course_slug}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Authorization': 'Bearer ' + (cookies_dict.get('access_token', '') or ''),
        }
        
        # محاولة بدون Authorization أولاً
        bc_response = client.get(bc_url, headers={
            'Accept': 'application/json',
            'Origin': 'https://yanfaa.com',
            'Referer': f'https://yanfaa.com/us/single/{course_slug}',
        })
        
        if bc_response.status_code == 200:
            bc_data = bc_response.json()
            sources = bc_data.get('sources', [])
            
            hls_url = None
            for source in sources:
                src = source.get('src', '')
                if '.m3u8' in src or 'application/x-mpegURL' in source.get('type', ''):
                    hls_url = src
                    break
            
            if hls_url:
                print(f"   ✅ تم العثور على HLS URL من Brightcove API")
                hls_urls_found.append({
                    'title': title,
                    'hls_url': hls_url,
                    'yanfaa_id': yanfaa_video_id
                })
                print(f"   📝 HLS URL: {hls_url[:80]}...")
                
                # محاولة التحميل باستخدام yt-dlp مع cookies
                safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
                safe_title = re.sub(r'\s+', '_', safe_title)
                filename_template = str(output_dir / f"{safe_title}.%(ext)s")
                
                # إنشاء ملف cookies Netscape
                netscape_cookies_file = output_dir / "cookies.txt"
                with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
                    f.write("# Netscape HTTP Cookie File\n\n")
                    for name, value in cookies_dict.items():
                        f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
                
                # تحميل باستخدام yt-dlp مباشرة على HLS URL
                cmd = [
                    sys.executable, '-m', 'yt_dlp',
                    '--cookies', str(netscape_cookies_file),
                    '--referer', f'https://yanfaa.com/us/single/{course_slug}',
                    '-o', filename_template,
                    hls_url
                ]
                
                print(f"   📥 بدء التحميل باستخدام yt-dlp...")
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=600
                )
                
                if process.returncode == 0:
                    downloaded.append(title)
                    print(f"   ✅ تم التحميل بنجاح!\n")
                else:
                    error_msg = process.stderr or process.stdout
                    errors.append(f"{title}: yt-dlp error - {error_msg[:150]}")
                    print(f"   ❌ فشل yt-dlp: {error_msg[:150]}\n")
            else:
                errors.append(f"{title}: لم يتم العثور على HLS URL في مصادر Brightcove")
                print(f"   ❌ لم يتم العثور على HLS URL\n")
        else:
            print(f"   ⚠️ Brightcove API رد بـ {bc_response.status_code}")
            print(f"   💡 قد نحتاج إلى استخراج HLS URLs مباشرة من network requests\n")
            errors.append(f"{title}: Brightcove API {bc_response.status_code}")
        
        client.close()
    
    except httpx.HTTPStatusError as e:
        errors.append(f"{title}: HTTP {e.response.status_code}")
        print(f"   ❌ خطأ HTTP: {e.response.status_code}\n")
    
    except Exception as e:
        errors.append(f"{title}: {str(e)}")
        print(f"   ❌ خطأ: {str(e)}\n")

# حفظ HLS URLs للاستخدام لاحقاً
if hls_urls_found:
    hls_urls_file = output_dir / "hls_urls.json"
    with open(hls_urls_file, 'w', encoding='utf-8') as f:
        json.dump(hls_urls_found, f, indent=2, ensure_ascii=False)
    print(f"✅ تم حفظ {len(hls_urls_found)} HLS URLs إلى {hls_urls_file}\n")

# عرض النتائج
print("="*60)
print(f"📊 النتائج:")
print(f"✅ تم تحميل: {len(downloaded)} فيديو")
print(f"❌ فشل: {len(errors)} فيديو")

if downloaded:
    print("\n✅ الفيديوهات المحمّلة:")
    for title in downloaded:
        print(f"   - {title}")

print("\n" + "="*60)

