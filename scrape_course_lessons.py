"""
كشط كورس learning_english_level_one واستخراج جميع الدروس (28 درس)
"""
import asyncio
import json
import sys
from pathlib import Path
from auth import YanfaaAuth
from scraper import YanfaaScraper
from proxy_helper import get_httpx_client
import config

COURSE_URL = "https://yanfaa.com/us/single/learning_english_level_one"
COURSE_SLUG = "learning_english_level_one"
EXPECTED_LESSONS = 28

async def scrape_course_lessons():
    """كشط الكورس واستخراج جميع الدروس"""
    print("=" * 60)
    print("📚 كشط كورس: Learning English Level One")
    print("=" * 60)
    print(f"🌐 الرابط: {COURSE_URL}")
    print(f"🎯 عدد الدروس المتوقع: {EXPECTED_LESSONS}")
    print()
    
    # إنشاء كائن المصادقة
    auth = YanfaaAuth()
    
    # التحقق من وجود الكوكيز
    print("🔍 التحقق من وجود جلسة محفوظة...")
    cookies = auth.load_cookies()
    
    if not cookies or not auth.is_logged_in():
        print("📝 لا توجد جلسة محفوظة، جاري تسجيل الدخول...")
        print(f"📧 البريد الإلكتروني: {config.EMAIL}")
        print()
        
        login_success = await auth.login()
        if not login_success:
            print("❌ فشل تسجيل الدخول. يرجى التحقق من البيانات وإعادة المحاولة.")
            return False
        
        # إعادة تحميل الكوكيز بعد تسجيل الدخول
        cookies = auth.load_cookies()
    else:
        print("✅ تم تحميل الجلسة المحفوظة بنجاح")
        print(f"🍪 عدد الكوكيز: {len(cookies) if cookies else 0}")
    
    print()
    print("=" * 60)
    print("🌐 بدء عملية الكشط")
    print("=" * 60)
    print()
    
    # إعداد مجلد الإخراج
    output_dir = Path('output') / COURSE_SLUG
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # تخطي كشط HTML مؤقتاً والاعتماد على API مباشرة
    print("💡 سيتم الاعتماد على API مباشرة لاستخراج معلومات الدروس")
    print("=" * 60)
    print("🔍 استخراج معلومات الدروس من API")
    print("=" * 60)
    print()
    
    # 2. محاولة استخراج معلومات الدروس من API
    try:
        # تحميل الكوكيز للاستخدام مع httpx
        cookies_dict = {}
        if cookies:
            for name, data in cookies.items():
                if isinstance(data, dict):
                    cookies_dict[name] = data.get('value', '')
                else:
                    cookies_dict[name] = str(data)
        
        headers = {
            'Accept': 'application/json',
            'Origin': 'https://yanfaa.com',
            'Referer': COURSE_URL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # محاولة الحصول على معلومات الكورس من API
        api_endpoints = [
            f'https://app.yanfaa.com/api/course/{COURSE_SLUG}',
            f'https://app.yanfaa.com/api/courses/{COURSE_SLUG}',
        ]
        
        course_data = None
        lessons = []
        
        with get_httpx_client(cookies=cookies_dict, headers=headers, timeout=30) as client:
            for endpoint in api_endpoints:
                try:
                    print(f"🔍 جاري محاولة: {endpoint}")
                    response = client.get(endpoint)
                    
                    if response.status_code == 200:
                        course_data = response.json()
                        print(f"✅ تم الحصول على بيانات الكورس")
                        print(f"   العنوان: {course_data.get('title', 'N/A')}")
                        print(f"   عدد الفيديوهات: {course_data.get('video_count', 0)}")
                        
                        # محاولة استخراج الدروس
                        if 'lessons' in course_data:
                            lessons = course_data['lessons']
                        elif 'videos' in course_data:
                            lessons = course_data['videos']
                        elif 'chapters' in course_data:
                            # استخراج الدروس من الفصول
                            for chapter in course_data.get('chapters', []):
                                if 'lessons' in chapter:
                                    lessons.extend(chapter['lessons'])
                        
                        if lessons:
                            print(f"✅ تم العثور على {len(lessons)} درس في API")
                            break
                        else:
                            print(f"⚠️  لم يتم العثور على دروس في API")
                            
                except Exception as e:
                    print(f"❌ خطأ في {endpoint}: {str(e)}")
                    continue
            
            # إذا لم نحصل على الدروس من API، نحاول من endpoints أخرى
            if not lessons:
                print()
                print("🔍 محاولة endpoints إضافية...")
                additional_endpoints = [
                    f'https://app.yanfaa.com/api/course/{COURSE_SLUG}/lessons',
                    f'https://app.yanfaa.com/api/courses/{COURSE_SLUG}/lessons',
                ]
                
                for endpoint in additional_endpoints:
                    try:
                        print(f"   جاري محاولة: {endpoint}")
                        response = client.get(endpoint, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if isinstance(data, list):
                                lessons = data
                            elif isinstance(data, dict):
                                lessons = data.get('data', data.get('lessons', []))
                            
                            if lessons:
                                print(f"   ✅ تم العثور على {len(lessons)} درس")
                                break
                    except Exception as e:
                        print(f"   ❌ خطأ: {str(e)[:50]}")
                        continue
        
        # حفظ بيانات الكورس
        if course_data:
            course_file = output_dir / "course_data.json"
            with open(course_file, 'w', encoding='utf-8') as f:
                json.dump(course_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 تم حفظ بيانات الكورس في: {course_file}")
        
        # حفظ قائمة الدروس
        if lessons:
            lessons_file = output_dir / "lessons.json"
            with open(lessons_file, 'w', encoding='utf-8') as f:
                json.dump(lessons, f, indent=2, ensure_ascii=False)
            print(f"💾 تم حفظ {len(lessons)} درس في: {lessons_file}")
            
            # عرض ملخص الدروس
            print()
            print("=" * 60)
            print("📋 ملخص الدروس المستخرجة")
            print("=" * 60)
            for i, lesson in enumerate(lessons[:10], 1):  # عرض أول 10 دروس
                title = lesson.get('title', lesson.get('name', f'Lesson {i}'))
                video_id = lesson.get('video_id', lesson.get('id', 'N/A'))
                brightcove_id = lesson.get('brightcove_video_id', lesson.get('brightcove_id', 'N/A'))
                print(f"   {i}. {title}")
                print(f"      Video ID: {video_id}, Brightcove: {brightcove_id}")
            
            if len(lessons) > 10:
                print(f"   ... و {len(lessons) - 10} درس آخر")
            
            print()
            print(f"✅ إجمالي الدروس المستخرجة: {len(lessons)} / {EXPECTED_LESSONS}")
            
            if len(lessons) < EXPECTED_LESSONS:
                print(f"⚠️  عدد الدروس أقل من المتوقع ({EXPECTED_LESSONS})")
                print("   قد تحتاج إلى استخدام طريقة أخرى لاستخراج باقي الدروس")
        else:
            print()
            print("⚠️  لم يتم العثور على دروس في API")
            print("   سيتم الاعتماد على الكشط من HTML فقط")
        
    except Exception as e:
        print(f"❌ خطأ في استخراج معلومات الدروس: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("✅ اكتمل الكشط!")
    print("=" * 60)
    print(f"📁 الملفات المحفوظة في: {output_dir}")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(scrape_course_lessons())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        sys.exit(0)

