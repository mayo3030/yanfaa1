"""
استخراج جميع video IDs من network requests وتحميلها بشكل متوازي (Turbo Speed)
"""
import json
import subprocess
import sys
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import httpx

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

print("="*60)
print("🚀 استخراج وتحميل جميع الفيديوهات (Turbo Mode)")
print("="*60)

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

print(f"\n📊 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: 29 فيديو\n")

if len(existing_videos) < 29:
    print("⚠️ لا توجد جميع video IDs بعد.")
    print("💡 يجب استخراج video IDs من network requests عند النقر على الدروس.")
    print("\n📋 الطريقة:")
    print("1. افتح المتصفح واذهب إلى صفحة الكورس")
    print("2. افتح DevTools > Network tab")
    print("3. انقر على كل درس (1-29)")
    print("4. ابحث عن: edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{VIDEO_ID}")
    print("5. انسخ VIDEO_ID لكل درس")
    print("\n💡 أو يمكنك استخدام browser automation لتسريع العملية.\n")
    
    # عرض الفيديوهات الموجودة
    if existing_videos:
        print("✅ الفيديوهات الموجودة:")
        for i, v in enumerate(existing_videos, 1):
            print(f"   {i}. {v['title']} - Brightcove: {v['brightcove_video_id']}")
    
    response = input("\nهل تريد المتابعة بتحميل الفيديوهات الموجودة فقط؟ (y/n): ")
    if response.lower() != 'y':
        print("✅ تم الإلغاء. يرجى استخراج جميع video IDs أولاً.")
        sys.exit(0)

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

# إنشاء Netscape cookies file
netscape_cookies_file = output_dir / "cookies.txt"
with open(netscape_cookies_file, 'w', encoding='utf-8') as f:
    f.write("# Netscape HTTP Cookie File\n\n")
    for name, value in cookies_dict.items():
        f.write(f".yanfaa.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")

def download_video(video_info):
    """تحميل فيديو واحد"""
    brightcove_id = video_info.get('brightcove_video_id', '')
    title = video_info.get('title', 'Unknown')
    
    if not brightcove_id:
        return {
            'status': 'error',
            'title': title,
            'error': 'No Brightcove ID'
        }
    
    # تنظيف العنوان
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
    safe_title = re.sub(r'\s+', '_', safe_title)
    
    # فحص الملف الموجود
    for ext in ['mp4', 'mkv', 'webm']:
        existing_file = output_dir / f"{safe_title}.{ext}"
        if existing_file.exists():
            file_size = existing_file.stat().st_size / (1024 * 1024)
            if file_size < 100:  # إذا كان أصغر من 100 MB
                return {
                    'status': 'skipped',
                    'title': title,
                    'reason': f'Already exists ({file_size:.2f} MB)'
                }
            elif file_size > 100:  # إذا كان كبيراً جداً، احذفه
                existing_file.unlink()
                break
    
    try:
        # استخدام Brightcove player URL
        video_url = f"https://players.brightcove.net/6164421959001/default_default/index.html?videoId={brightcove_id}"
        output_template = str(output_dir / f"{safe_title}.%(ext)s")
        
        # yt-dlp مع جودة 480p
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--cookies', str(netscape_cookies_file),
            '--referer', course_url,
            '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '--merge-output-format', 'mp4',
            '--no-warnings',
            '--no-playlist',
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
        
        # التحقق من الملف
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
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'status': 'error',
            'title': title,
            'error': str(e)
        }

# بدء التحميل المتوازي
print(f"\n🚀 بدء تحميل {len(existing_videos)} فيديو بشكل متوازي (Turbo Mode)...\n")
start_time = time.time()

max_workers = 5  # عدد الـ threads المتوازية
results = {'success': [], 'error': [], 'skipped': []}

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_video = {executor.submit(download_video, video): video for video in existing_videos}
    
    completed = 0
    total = len(existing_videos)
    
    for future in as_completed(future_to_video):
        completed += 1
        video = future_to_video[future]
        
        try:
            result = future.result()
            result['video'] = video.get('title', 'Unknown')
            
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
                'title': video.get('title', 'Unknown'),
                'error': str(e)
            }
            results['error'].append(error_result)
            print(f"❌ [{completed}/{total}] {video.get('title', 'Unknown')} - Exception: {str(e)}")

elapsed_time = time.time() - start_time

# عرض النتائج
print("\n" + "="*60)
print("📊 النتائج النهائية:")
print(f"✅ نجح: {len(results['success'])} فيديو")
print(f"⏭️  تم التخطي: {len(results['skipped'])} فيديو")
print(f"❌ فشل: {len(results['error'])} فيديو")
print(f"⏱️  الوقت: {elapsed_time/60:.2f} دقيقة")
print("="*60)

if results['success']:
    total_size = sum(item.get('file_size_mb', 0) for item in results['success'])
    print(f"\n📦 الحجم الإجمالي: {total_size:.2f} MB ({total_size/1024:.2f} GB)")

# حفظ النتائج
results_file = output_dir / "download_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'success': len(results['success']),
            'skipped': len(results['skipped']),
            'error': len(results['error']),
            'total_time_seconds': elapsed_time
        },
        'results': results
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 تم حفظ النتائج في: {results_file}")



