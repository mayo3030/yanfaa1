"""
تحميل جميع الفيديوهات بشكل متوازي (Turbo Speed) باستخدام ThreadPoolExecutor
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قراءة video IDs
video_ids_file = output_dir / "extracted_video_ids.json"
if not video_ids_file.exists():
    print(f"❌ ملف {video_ids_file} غير موجود. يرجى استخراج video IDs أولاً.")
    sys.exit(1)

with open(video_ids_file, 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"📚 جاهز لتحميل {len(videos)} فيديو بشكل متوازي (Turbo Mode)\n")

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

# إنشاء Netscape cookies file
netscape_cookies_file = output_dir / "cookies.txt"
with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
    f.write("# Netscape HTTP Cookie File\n\n")
    for name, value in cookies_dict.items():
        f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")

# HLS URLs من network requests (إذا كانت متوفرة)
hls_urls_map = {
    1136: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/20a5f2e1-822b-4c07-ba10-f32608bb58af/10s/master.m3u8?fastly_token=NjkzMmIwNmNfMDYwMWYwMmZmOGZkMGZhNzM0MjA4OTJkMDVjNmI5ZDc1ZDY0YWUwYjU1NDM5OGJjZmUwMDk5MGQwYTU4MmQ5Yw%3D%3D",
    1137: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/ca342b83-0700-4fa3-a17d-7d3fa5d3b9e3/10s/master.m3u8?fastly_token=NjkzMmIxYmRfNjY5ZjZmZjQ1MzhlYjI3NmQ0MzM3OTQ1ZDg5MDljZWRkYjUyNGE5MTg5NmMyMTFjODZmZjc2MjQ1NWY1Y2VkZg%3D%3D",
    1138: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/5c8cb696-6f39-4ee5-99e3-330d97b1965b/10s/master.m3u8?fastly_token=NjkzMmIyMzFfMGM4NDE3YTVhYjk0MGYzNDA2ZjRlNTQ5YTQ2ZTIyNWU3OTFmNTNlODkzNmM4YTdmMGRlMDkzYmU1OWJhOWQxMQ%3D%3D",
    1139: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a0c7713c-f8c8-4d1d-b582-8ab98027dbb3/10s/master.m3u8?fastly_token=NjkzMmIwNWFfYTdiY2UzYTNiYmIzZWY2NGExZGZmMjY4YTEzZDcxYjkwMmM1NjgzNDJkYWYzZTM4MjcxNjE5ZjlkOTA1MmRjNw%3D%3D",
    1146: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/c08b0e39-7af8-4da0-9563-3182828845cf/10s/master.m3u8?fastly_token=NjkzMmIxZGVfMzNjMTk2NDQ0OGE1YjE2YTc2ZjdhM2QwYWUwYTEyOTgwOTNiZDFjOTA2Y2NlNzQwYWUwMWE2NmVhZTQwNTBiOQ%3D%3D",
    1149: "https://manifest.prod.boltdns.net/manifest/v1/hls/v4/aes128/6164421959001/a10d4e32-dc35-4629-9898-aee424720d0c/10s/master.m3u8?fastly_token=NjkzMmIwYzhfNTAzODIzMzk2ZjQwNTMwNTViY2EzYjJhMTEzOGU4M2IzZjJlZDg5Y2ZmOGIyNjVjMDBjZmZkN2NlYzg4MTBlNQ%3D%3D"
}

def download_video(video_info):
    """تحميل فيديو واحد"""
    yanfaa_video_id = video_info['yanfaa_video_id']
    brightcove_id = video_info.get('brightcove_video_id', '')
    title = video_info['title']
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    
    # فحص الملف الموجود
    for ext in ['mp4', 'mkv', 'webm']:
        existing_file = output_dir / f"{safe_title}.{ext}"
        if existing_file.exists():
            file_size = existing_file.stat().st_size / (1024 * 1024)
            # إذا كان الملف موجوداً وأصغر من 100 MB، تخطي
            if file_size < 100:
                return {'status': 'skipped', 'title': title, 'reason': f'Already exists ({file_size:.2f} MB)'}
            # إذا كان كبيراً جداً، احذفه وأعد التحميل
            elif file_size > 100:
                existing_file.unlink()
                break
    
    try:
        # استخدام Brightcove player URL مع yt-dlp
        video_url = f"https://players.brightcove.net/6164421959001/default_default/index.html?videoId={brightcove_id}"
        
        # أو استخدام HLS URL مباشرة إذا كان متوفراً
        hls_url = hls_urls_map.get(yanfaa_video_id)
        if hls_url:
            video_url = hls_url
        
        output_template = str(output_dir / f"{safe_title}.%(ext)s")
        
        # yt-dlp command مع جودة 480p لتقليل الحجم
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--cookies', str(netscape_cookies_file),
            '--referer', f'https://yanfaa.com/us/single/{course_slug}',
            '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '--merge-output-format', 'mp4',
            '--no-warnings',
            '--no-playlist',
            '--progress', '--progress-template', '%(progress.downloaded_bytes)s/%(progress.total_bytes)s',
            '-o', output_template,
            video_url
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=600
        )
        
        # التحقق من الملف المحمّل
        for ext in ['mp4', 'mkv', 'webm']:
            downloaded_file = output_dir / f"{safe_title}.{ext}"
            if downloaded_file.exists():
                file_size = downloaded_file.stat().st_size / (1024 * 1024)
                return {
                    'status': 'success',
                    'title': title,
                    'file_size_mb': file_size,
                    'file': str(downloaded_file)
                }
        
        # إذا لم يتم العثور على ملف
        error_msg = process.stderr[-200:] if process.stderr else process.stdout[-200:] or "Unknown error"
        return {
            'status': 'error',
            'title': title,
            'error': error_msg[:150]
        }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'title': title,
            'error': 'Timeout after 10 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'title': title,
            'error': str(e)
        }

# تحميل الفيديوهات بشكل متوازي
print("🚀 بدء التحميل المتوازي (Turbo Mode)...\n")
start_time = time.time()

# استخدام ThreadPoolExecutor مع 5 threads متوازية (يمكن زيادة العدد)
max_workers = 5  # يمكن زيادتها إلى 10 أو أكثر حسب سرعة الإنترنت

results = {
    'success': [],
    'error': [],
    'skipped': []
}

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # إرسال جميع مهام التحميل
    future_to_video = {executor.submit(download_video, video): video for video in videos}
    
    # تتبع التقدم
    completed = 0
    total = len(videos)
    
    for future in as_completed(future_to_video):
        completed += 1
        video = future_to_video[future]
        
        try:
            result = future.result()
            result['video'] = video['title']
            
            if result['status'] == 'success':
                results['success'].append(result)
                print(f"✅ [{completed}/{total}] {result['title']} ({result['file_size_mb']:.2f} MB)")
            elif result['status'] == 'skipped':
                results['skipped'].append(result)
                print(f"⏭️  [{completed}/{total}] {result['title']} - {result['reason']}")
            else:
                results['error'].append(result)
                print(f"❌ [{completed}/{total}] {result['title']} - {result['error'][:80]}")
        
        except Exception as e:
            error_result = {
                'status': 'error',
                'title': video['title'],
                'error': str(e)
            }
            results['error'].append(error_result)
            print(f"❌ [{completed}/{total}] {video['title']} - Exception: {str(e)}")

elapsed_time = time.time() - start_time

# عرض النتائج النهائية
print("\n" + "="*60)
print("📊 النتائج النهائية:")
print(f"✅ نجح: {len(results['success'])} فيديو")
print(f"⏭️  تم التخطي: {len(results['skipped'])} فيديو")
print(f"❌ فشل: {len(results['error'])} فيديو")
print(f"⏱️  الوقت المستغرق: {elapsed_time/60:.2f} دقيقة ({elapsed_time:.0f} ثانية)")
print("="*60)

if results['success']:
    print("\n✅ الفيديوهات المحمّلة بنجاح:")
    total_size = 0
    for item in results['success']:
        size = item.get('file_size_mb', 0)
        total_size += size
        print(f"   - {item['title']} ({size:.2f} MB)")
    print(f"\n📦 الحجم الإجمالي: {total_size:.2f} MB ({total_size/1024:.2f} GB)")

if results['skipped']:
    print(f"\n⏭️  الفيديوهات المتخطاة ({len(results['skipped'])}):")
    for item in results['skipped'][:5]:  # عرض أول 5 فقط
        print(f"   - {item['title']}: {item['reason']}")

if results['error']:
    print(f"\n❌ الأخطاء ({len(results['error'])}):")
    for item in results['error'][:10]:  # عرض أول 10 أخطاء فقط
        print(f"   - {item['title']}: {item['error'][:100]}")

# حفظ النتائج في ملف JSON
results_file = output_dir / "download_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'success': len(results['success']),
            'skipped': len(results['skipped']),
            'error': len(results['error']),
            'total_time_seconds': elapsed_time,
            'total_time_minutes': elapsed_time / 60
        },
        'results': results
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 تم حفظ النتائج في: {results_file}")



