"""
كشط جميع الدروس (28 درس) باستخدام browser automation
النقر على كل درس واستخراج معلوماته
"""
import asyncio
import json
import sys
from pathlib import Path
from auth import YanfaaAuth
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode
from proxy_helper import get_httpx_client
import config

COURSE_URL = "https://yanfaa.com/us/single/learning_english_level_one"
COURSE_SLUG = "learning_english_level_one"
EXPECTED_LESSONS = 28

async def scrape_all_lessons():
    """كشط جميع الدروس باستخدام browser automation"""
    print("=" * 60)
    print("📚 كشط جميع دروس الكورس")
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
        login_success = await auth.login()
        if not login_success:
            print("❌ فشل تسجيل الدخول")
            return False
        cookies = auth.load_cookies()
    else:
        print("✅ تم تحميل الجلسة المحفوظة")
    
    print()
    print("=" * 60)
    print("🌐 بدء عملية الكشط")
    print("=" * 60)
    print()
    
    # إعداد مجلد الإخراج
    output_dir = Path('output') / COURSE_SLUG
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # إعداد البروكسي
    proxy_config = None
    if config.PROXY_ENABLED and config.PROXY_URL:
        proxy_config = config.PROXY_URL
        print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
        print()
    
    browser_config = BrowserConfig(
        headless=False,  # عرض المتصفح لرؤية ما يحدث
        verbose=True,
        proxy_config=proxy_config
    )
    
    all_lessons = []
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"🔍 جاري فتح صفحة الكورس...")
            print(f"   URL: {COURSE_URL}")
            print()
            
            # فتح صفحة الكورس
            result = await crawler.arun(
                url=COURSE_URL,
                word_count_threshold=10,
                cache_mode=CacheMode.BYPASS,
                wait_for="domcontentloaded",
                js_code="""
                // انتظار تحميل الصفحة
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                // البحث عن قائمة الدروس
                // عادة تكون في sidebar أو قائمة
                let lessonElements = [];
                
                // محاولة العثور على عناصر الدروس
                // قد تكون في: .lesson, .lesson-item, [data-lesson-id], etc.
                let selectors = [
                    '.lesson',
                    '.lesson-item',
                    '[data-lesson-id]',
                    '.course-lesson',
                    'li[class*="lesson"]',
                    'div[class*="lesson"]',
                    'a[href*="lesson"]',
                    '.sidebar li',
                    '.lessons-list li',
                    '.course-content li'
                ];
                
                for (let selector of selectors) {
                    let elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        lessonElements = Array.from(elements);
                        console.log(`Found ${elements.length} lessons with selector: ${selector}`);
                        break;
                    }
                }
                
                // إذا لم نجد، نحاول البحث في كل العناصر
                if (lessonElements.length === 0) {
                    // البحث عن أي عنصر يحتوي على رقم أو عنوان درس
                    let allElements = document.querySelectorAll('li, div, a');
                    for (let el of allElements) {
                        let text = el.textContent || el.innerText || '';
                        // البحث عن نمط مثل "Lesson 1", "1.", "درس 1", etc.
                        if (/\\d+/.test(text) && text.length < 100) {
                            lessonElements.push(el);
                        }
                    }
                }
                
                return {
                    lessonCount: lessonElements.length,
                    pageTitle: document.title,
                    url: window.location.href
                };
                """
            )
            
            if result.success:
                print("✅ تم فتح صفحة الكورس")
                print()
                
                # محاولة استخراج معلومات الدروس من JavaScript
                print("🔍 جاري استخراج معلومات الدروس...")
                
                extract_lessons_js = """
                // استخراج معلومات الدروس
                let lessons = [];
                
                // البحث عن عناصر الدروس
                let lessonSelectors = [
                    '.lesson',
                    '.lesson-item',
                    '[data-lesson-id]',
                    '.course-lesson',
                    'li[class*="lesson"]',
                    'div[class*="lesson"]'
                ];
                
                let lessonElements = [];
                for (let selector of lessonSelectors) {
                    let elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        lessonElements = Array.from(elements);
                        break;
                    }
                }
                
                // إذا لم نجد، نبحث في sidebar
                if (lessonElements.length === 0) {
                    let sidebar = document.querySelector('.sidebar, .course-sidebar, .lessons-sidebar');
                    if (sidebar) {
                        lessonElements = Array.from(sidebar.querySelectorAll('li, div, a'));
                    }
                }
                
                // استخراج معلومات كل درس
                lessonElements.forEach((el, index) => {
                    let title = el.textContent?.trim() || el.innerText?.trim() || `Lesson ${index + 1}`;
                    let href = el.href || el.querySelector('a')?.href || '';
                    let lessonId = el.getAttribute('data-lesson-id') || 
                                   el.getAttribute('data-id') || 
                                   el.id || 
                                   (index + 1).toString();
                    
                    lessons.push({
                        index: index + 1,
                        title: title.substring(0, 200), // تقليل الطول
                        href: href,
                        lessonId: lessonId
                    });
                });
                
                return {
                    lessons: lessons,
                    total: lessons.length
                };
                """
                
                lessons_result = await crawler.arun(
                    url=COURSE_URL,
                    js_code=extract_lessons_js,
                    word_count_threshold=1,
                    wait_for="domcontentloaded"
                )
                
                if lessons_result.success:
                    # محاولة استخراج البيانات من النتيجة
                    print("✅ تم استخراج معلومات الدروس")
                    
                    # حفظ HTML للفحص
                    html_file = output_dir / "course_page.html"
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(lessons_result.html or '')
                    print(f"💾 تم حفظ HTML في: {html_file}")
                
                # محاولة الحصول على معلومات من API أيضاً
                print()
                print("🔍 جاري الحصول على معلومات من API...")
                
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
                
                with get_httpx_client(cookies=cookies_dict, headers=headers, timeout=30) as client:
                    # محاولة الحصول على معلومات الكورس
                    api_url = f'https://app.yanfaa.com/api/course/{COURSE_SLUG}'
                    try:
                        response = client.get(api_url)
                        if response.status_code == 200:
                            course_data = response.json()
                            
                            # حفظ بيانات الكورس
                            course_file = output_dir / "course_data.json"
                            with open(course_file, 'w', encoding='utf-8') as f:
                                json.dump(course_data, f, indent=2, ensure_ascii=False)
                            
                            print(f"✅ تم الحصول على بيانات الكورس من API")
                            print(f"   العنوان: {course_data.get('title', 'N/A')}")
                            print(f"   عدد الفيديوهات: {course_data.get('video_count', 0)}")
                            
                            # محاولة استخراج الدروس
                            if 'lessons' in course_data:
                                all_lessons = course_data['lessons']
                            elif 'videos' in course_data:
                                all_lessons = course_data['videos']
                            
                    except Exception as e:
                        print(f"⚠️  خطأ في API: {str(e)}")
                
                # حفظ النتائج
                if all_lessons:
                    lessons_file = output_dir / "all_lessons.json"
                    with open(lessons_file, 'w', encoding='utf-8') as f:
                        json.dump(all_lessons, f, indent=2, ensure_ascii=False)
                    
                    print()
                    print("=" * 60)
                    print("📋 ملخص الدروس")
                    print("=" * 60)
                    for i, lesson in enumerate(all_lessons[:10], 1):
                        title = lesson.get('title', lesson.get('name', f'Lesson {i}'))
                        video_id = lesson.get('video_id', lesson.get('id', 'N/A'))
                        print(f"   {i}. {title} (ID: {video_id})")
                    
                    if len(all_lessons) > 10:
                        print(f"   ... و {len(all_lessons) - 10} درس آخر")
                    
                    print()
                    print(f"✅ إجمالي الدروس: {len(all_lessons)} / {EXPECTED_LESSONS}")
                else:
                    print()
                    print("⚠️  لم يتم العثور على دروس في API")
                    print("   قد تحتاج إلى استخدام طريقة أخرى")
                
            else:
                print(f"❌ فشل فتح صفحة الكورس: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("✅ اكتمل الكشط!")
    print("=" * 60)
    print(f"📁 الملفات المحفوظة في: {output_dir}")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(scrape_all_lessons())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        sys.exit(0)



