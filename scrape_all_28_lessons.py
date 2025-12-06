"""
كشط واستخراج جميع الدروس (28 درس) من كورس learning_english_level_one
"""
import json
import sys
from pathlib import Path
from proxy_helper import get_httpx_client
import config

COURSE_SLUG = "learning_english_level_one"
COURSE_ID = 69
EXPECTED_LESSONS = 28

def load_existing_data():
    """تحميل البيانات الموجودة"""
    output_dir = Path('output') / COURSE_SLUG / 'videos'
    existing_videos = []
    
    # تحميل extracted_video_ids.json
    extracted_file = output_dir / "extracted_video_ids.json"
    if extracted_file.exists():
        with open(extracted_file, 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
    
    return existing_videos, output_dir

def get_session_id_from_cookies():
    """الحصول على session_id من الكوكيز"""
    cookies_file = Path('cookies.json')
    if not cookies_file.exists():
        cookies_file = Path('cookies_yanfaa_account.json')
    
    if cookies_file.exists():
        with open(cookies_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            # البحث عن session_id
            for name, value in cookies.items():
                if 'session' in name.lower():
                    if isinstance(value, dict):
                        return value.get('value', '')
                    return str(value)
    
    return None

def scrape_all_lessons():
    """كشط جميع الدروس"""
    print("=" * 60)
    print("📚 كشط جميع دروس الكورس")
    print("=" * 60)
    print(f"📖 الكورس: {COURSE_SLUG}")
    print(f"🎯 عدد الدروس المتوقع: {EXPECTED_LESSONS}")
    print()
    
    # تحميل البيانات الموجودة
    existing_videos, output_dir = load_existing_data()
    print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")
    if existing_videos:
        print("الدروس الموجودة:")
        for v in existing_videos[:5]:
            print(f"   - {v.get('title', 'N/A')} (ID: {v.get('yanfaa_video_id', 'N/A')})")
        if len(existing_videos) > 5:
            print(f"   ... و {len(existing_videos) - 5} درس آخر")
    print()
    
    # الحصول على session_id
    session_id = get_session_id_from_cookies()
    if not session_id:
        print("⚠️  لم يتم العثور على session_id في الكوكيز")
        print("   سيتم المحاولة بدون session_id")
        session_id = ''
    
    # إعداد headers
    headers = {
        'Accept': 'application/json',
        'Origin': 'https://yanfaa.com',
        'Referer': f'https://yanfaa.com/us/single/{COURSE_SLUG}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # تحميل الكوكيز
    cookies_dict = {}
    cookies_file = Path('cookies.json')
    if not cookies_file.exists():
        cookies_file = Path('cookies_yanfaa_account.json')
    
    if cookies_file.exists():
        with open(cookies_file, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
            for name, data in cookies_data.items():
                if isinstance(data, dict):
                    cookies_dict[name] = data.get('value', '')
                else:
                    cookies_dict[name] = str(data)
    
    all_lessons = []
    # إضافة الفيديوهات الموجودة أولاً
    found_video_ids = set()
    for video in existing_videos:
        video_id = video.get('yanfaa_video_id')
        if video_id:
            all_lessons.append(video)
            found_video_ids.add(video_id)
    
    print("=" * 60)
    print("🔍 استخراج معلومات الدروس")
    print("=" * 60)
    print()
    
    with get_httpx_client(cookies=cookies_dict, headers=headers, timeout=30) as client:
        # 1. الحصول على معلومات الكورس
        print("1️⃣ جاري الحصول على معلومات الكورس...")
        api_url = f'https://app.yanfaa.com/api/course/{COURSE_SLUG}'
        if session_id:
            api_url += f'?session_id={session_id}'
        
        try:
            response = client.get(api_url)
            if response.status_code == 200:
                course_data = response.json()
                print(f"   ✅ العنوان: {course_data.get('title', 'N/A')}")
                print(f"   ✅ عدد الفيديوهات: {course_data.get('video_count', 0)}")
                
                # حفظ بيانات الكورس
                course_file = output_dir.parent / "course_data.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(course_data, f, indent=2, ensure_ascii=False)
                print(f"   💾 تم الحفظ في: {course_file}")
                
                # إضافة الفيديو الموجود في API
                if 'videos' in course_data and course_data['videos']:
                    for video in course_data['videos']:
                        video_id = video.get('id')
                        if video_id and video_id not in found_video_ids:
                            all_lessons.append({
                                'yanfaa_video_id': video_id,
                                'brightcove_video_id': video.get('brightcove_video_id', ''),
                                'title': video.get('title', f'Video {video_id}'),
                                'duration': video.get('duration', 0),
                                'sort': video.get('sort', 0)
                            })
                            found_video_ids.add(video_id)
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
        
        print()
        
        # 2. عرض الفيديوهات المضافة
        print("2️⃣ الفيديوهات المضافة من البيانات الموجودة:")
        print(f"   ✅ إجمالي الدروس حتى الآن: {len(all_lessons)}")
        for video in all_lessons[:5]:
            print(f"      - {video.get('title', 'N/A')} (ID: {video.get('yanfaa_video_id', 'N/A')})")
        if len(all_lessons) > 5:
            print(f"      ... و {len(all_lessons) - 5} درس آخر")
        print()
        
        # 3. محاولة استخراج باقي الدروس من خلال مسح video IDs
        print("3️⃣ محاولة استخراج باقي الدروس من خلال مسح video IDs...")
        print(f"   🎯 المتبقي: {EXPECTED_LESSONS - len(all_lessons)} درس")
        print()
        
        # نطاق video IDs للمسح (بناءً على البيانات الموجودة)
        # الفيديوهات الموجودة: 1125, 1127, 1136, 1137, 1138, 1139, 1146, 1149
        # دعنا نمسح نطاق أوسع
        start_id = 1100
        end_id = 1300
        scanned_count = 0
        
        print(f"   🔍 مسح video IDs من {start_id} إلى {end_id}...")
        print(f"   ⏳ قد يستغرق هذا بعض الوقت...")
        print()
        
        for video_id in range(start_id, end_id + 1):
            if video_id in found_video_ids:
                continue
            
            try:
                video_url = f'https://app.yanfaa.com/api/videos/{video_id}'
                if session_id:
                    video_url += f'?session_id={session_id}'
                
                response = client.get(video_url, timeout=3)
                
                if response.status_code == 200:
                    video_data = response.json()
                    brightcove_id = video_data.get('brightcove_video_id') or video_data.get('video_id')
                    title = video_data.get('title', f'Video {video_id}')
                    course_id = video_data.get('course_id')
                    
                    # التحقق من أن الفيديو ينتمي لهذا الكورس
                    if course_id == COURSE_ID or str(course_id) == str(COURSE_ID):
                        lesson = {
                            'yanfaa_video_id': video_id,
                            'brightcove_video_id': brightcove_id or '',
                            'title': title,
                            'duration': video_data.get('duration', 0),
                            'sort': video_data.get('sort', video_id)
                        }
                        if video_id not in found_video_ids:
                            all_lessons.append(lesson)
                            found_video_ids.add(video_id)
                            scanned_count += 1
                            print(f"   ✅ [{scanned_count}] {title} (ID: {video_id}, Brightcove: {brightcove_id or 'N/A'})")
                            
                            if len(all_lessons) >= EXPECTED_LESSONS:
                                print(f"   🎉 تم العثور على جميع الدروس!")
                                break
                
                # تأخير بسيط لتجنب rate limiting
                if video_id % 10 == 0:
                    import time
                    time.sleep(0.1)
                    
            except Exception as e:
                # تجاهل الأخطاء (404 متوقع)
                pass
        
        print()
    
    # ترتيب الدروس حسب sort
    all_lessons.sort(key=lambda x: x.get('sort', x.get('yanfaa_video_id', 0)))
    
    # حفظ جميع الدروس
    lessons_file = output_dir / "all_lessons.json"
    with open(lessons_file, 'w', encoding='utf-8') as f:
        json.dump(all_lessons, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print("📋 ملخص النتائج")
    print("=" * 60)
    print(f"✅ إجمالي الدروس المستخرجة: {len(all_lessons)} / {EXPECTED_LESSONS}")
    print()
    
    if all_lessons:
        print("قائمة الدروس:")
        for i, lesson in enumerate(all_lessons, 1):
            title = lesson.get('title', f'Lesson {i}')
            video_id = lesson.get('yanfaa_video_id', 'N/A')
            brightcove_id = lesson.get('brightcove_video_id', 'N/A')
            print(f"   {i:2d}. {title}")
            print(f"       Yanfaa ID: {video_id}, Brightcove: {brightcove_id}")
    
    print()
    print(f"💾 تم حفظ جميع الدروس في: {lessons_file}")
    
    if len(all_lessons) < EXPECTED_LESSONS:
        print()
        print(f"⚠️  عدد الدروس ({len(all_lessons)}) أقل من المتوقع ({EXPECTED_LESSONS})")
        print("   قد تحتاج إلى:")
        print("   1. التحقق من session_id")
        print("   2. استخدام browser automation للنقر على كل درس")
        print("   3. استخراج video IDs من network requests")
    
    return len(all_lessons) >= EXPECTED_LESSONS

if __name__ == "__main__":
    try:
        success = scrape_all_lessons()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        sys.exit(0)

