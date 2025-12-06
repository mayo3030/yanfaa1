"""
🚀 سكريبت تلقائي كامل لتحميل جميع فيديوهات الكورس
- يفتح كل درس تلقائياً
- يجمع URLs الفيديو من network requests
- يحمل الفيديوهات باستخدام ffmpeg
"""
import json
import subprocess
import time
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
import config


def load_cookies(cookies_file="cookies_yanfaa_account.json"):
    """تحميل الكوكيز من الملف"""
    cookies_path = Path(cookies_file)
    if not cookies_path.exists():
        print(f"⚠️ ملف الكوكيز غير موجود: {cookies_file}")
        return None
    
    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        # تحويل تنسيق الكوكيز إلى تنسيق Playwright
        cookies_list = []
        for name, value in cookies_data.items():
            if isinstance(value, dict):
                cookie = {
                    'name': name,
                    'value': value.get('value', str(value)),
                    'domain': value.get('domain', '.yanfaa.com'),
                    'path': value.get('path', '/'),
                    'secure': value.get('secure', False),
                }
                if value.get('expiration'):
                    cookie['expires'] = value.get('expiration')
            else:
                cookie = {
                    'name': name,
                    'value': str(value),
                    'domain': '.yanfaa.com',
                    'path': '/',
                    'secure': False
                }
            cookies_list.append(cookie)
        
        print(f"✅ تم تحميل {len(cookies_list)} كوكيز")
        return cookies_list
    except Exception as e:
        print(f"❌ خطأ في تحميل الكوكيز: {e}")
        return None


def sanitize_filename(name):
    """تنظيف اسم الملف من الأحرف غير المسموحة"""
    # إزالة الأحرف الخاصة والاحتفاظ بالعربية والإنجليزية والأرقام
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    safe_name = safe_name.strip()
    # تقليل الطول
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    return safe_name


def login_with_playwright(page, context, email=None, password=None):
    """
    تسجيل الدخول إلى Yanfaa باستخدام Playwright
    
    Args:
        page: صفحة Playwright
        context: سياق المتصفح (لحفظ الكوكيز)
        email: البريد الإلكتروني (من config إذا لم يتم التحديد)
        password: كلمة المرور (من config إذا لم يتم التحديد)
    
    Returns:
        bool: True إذا نجح تسجيل الدخول
    """
    email = email or config.EMAIL
    password = password or config.PASSWORD
    login_url = config.LOGIN_URL
    
    print("🔐 جاري تسجيل الدخول...")
    print(f"📧 البريد: {email}")
    
    try:
        # الانتقال إلى صفحة تسجيل الدخول
        page.goto(login_url, wait_until="networkidle", timeout=60000)
        time.sleep(3)
        
        # البحث عن حقول الإدخال
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[id*="email" i]',
            'input[placeholder*="بريد" i]',
            'input[placeholder*="email" i]',
            'input[placeholder*="Email" i]'
        ]
        
        password_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[id*="password" i]',
            'input[placeholder*="كلمة" i]',
            'input[placeholder*="password" i]',
            'input[placeholder*="Password" i]'
        ]
        
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("تسجيل دخول")',
            'button:has-text("Login")',
            'button.btn-primary',
            'button[class*="login"]',
            'form button'
        ]
        
        # انتظار تحميل الصفحة بالكامل
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        # محاولة العثور على iframe إذا كان موجوداً
        target_page = page
        try:
            iframe = page.query_selector('iframe')
            if iframe:
                print("📦 تم العثور على iframe، جاري التبديل...")
                frame = iframe.content_frame()
                if frame:
                    target_page = frame
                    print("✅ تم التبديل إلى iframe")
                    time.sleep(2)
        except Exception as e:
            print(f"⚠️ خطأ في التعامل مع iframe: {e}")
        
        # العثور على حقل البريد الإلكتروني مع انتظار
        email_input = None
        for selector in email_selectors:
            try:
                email_input = target_page.wait_for_selector(selector, timeout=10000, state="visible")
                if email_input:
                    print(f"✅ تم العثور على حقل البريد: {selector}")
                    break
            except:
                continue
        
        # إذا لم نجد في iframe، جرب الصفحة الرئيسية
        if not email_input:
            print("🔍 البحث في الصفحة الرئيسية...")
            for selector in email_selectors:
                try:
                    email_input = page.wait_for_selector(selector, timeout=5000, state="visible")
                    if email_input:
                        print(f"✅ تم العثور على حقل البريد في الصفحة الرئيسية: {selector}")
                        target_page = page
                        break
                except:
                    continue
        
        if not email_input:
            print("❌ لم يتم العثور على حقل البريد الإلكتروني")
            # محاولة التقاط screenshot للتشخيص
            try:
                page.screenshot(path="login_debug.png")
                print("📸 تم حفظ screenshot في: login_debug.png")
            except:
                pass
            return False
        
        # العثور على حقل كلمة المرور مع انتظار
        password_input = None
        for selector in password_selectors:
            try:
                password_input = target_page.wait_for_selector(selector, timeout=10000, state="visible")
                if password_input:
                    print(f"✅ تم العثور على حقل كلمة المرور: {selector}")
                    break
            except:
                continue
        
        if not password_input:
            print("❌ لم يتم العثور على حقل كلمة المرور")
            return False
        
        # إدخال البيانات
        try:
            email_input.fill(email)
            time.sleep(0.5)
            
            password_input.fill(password)
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ خطأ في إدخال البيانات: {e}")
            # محاولة استخدام type بدلاً من fill
            try:
                email_input.click()
                email_input.type(email, delay=50)
                time.sleep(0.5)
                
                password_input.click()
                password_input.type(password, delay=50)
                time.sleep(0.5)
            except Exception as e2:
                print(f"❌ فشل إدخال البيانات: {e2}")
                return False
        
        # البحث عن checkbox "تذكرني" وتفعيله
        try:
            remember_checkbox = page.query_selector('input[type="checkbox"]')
            if remember_checkbox and not remember_checkbox.is_checked():
                remember_checkbox.check()
        except:
            pass
        
        time.sleep(0.5)
        
        # العثور على زر تسجيل الدخول والضغط عليه
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = target_page.query_selector(selector)
                if submit_button:
                    break
            except:
                continue
        
        if submit_button:
            submit_button.click()
        else:
            # محاولة الضغط على Enter
            password_input.press("Enter")
        
        # انتظار التوجيه أو تحميل الصفحة التالية
        print("⏳ انتظار تسجيل الدخول...")
        time.sleep(5)
        
        # التحقق من نجاح تسجيل الدخول
        current_url = page.url
        if "login" not in current_url.lower() or page.url != login_url:
            print("✅ تم تسجيل الدخول بنجاح!")
            
            # حفظ الكوكيز
            cookies = context.cookies()
            if cookies:
                cookies_file = Path("cookies_yanfaa_account.json")
                cookies_dict = {}
                for cookie in cookies:
                    cookies_dict[cookie['name']] = {
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.yanfaa.com'),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False),
                        'expiration': cookie.get('expires', None)
                    }
                
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
                print(f"💾 تم حفظ الكوكيز في: {cookies_file}")
            
            return True
        else:
            # التحقق من وجود رسالة خطأ
            try:
                error_msg = page.query_selector('.error, .alert-danger, [class*="error"]')
                if error_msg:
                    error_text = error_msg.inner_text()
                    print(f"❌ خطأ في تسجيل الدخول: {error_text}")
            except:
                pass
            
            print("❌ فشل تسجيل الدخول - لا يزال في صفحة تسجيل الدخول")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تسجيل الدخول: {e}")
        return False


def full_auto_download(course_url, output_folder="downloaded_videos", headless=False):
    """
    تحميل تلقائي كامل لجميع فيديوهات الكورس
    
    Args:
        course_url: رابط صفحة الكورس
        output_folder: مجلد الحفظ
        headless: إخفاء المتصفح (False لعرض المتصفح)
    """
    # إنشاء مجلد الحفظ
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    video_urls = {}  # {lesson_name: url}
    video_data = []  # [{name, url, lesson_index}]
    
    # تحميل الكوكيز
    cookies = load_cookies()
    
    print("="*60)
    print("🚀 بدء التحميل التلقائي الكامل")
    print("="*60)
    print(f"📚 رابط الكورس: {course_url}")
    print(f"💾 مجلد الحفظ: {output_folder}")
    print()
    
    with sync_playwright() as p:
        # إعداد البروكسي
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ignore_https_errors': True  # تجاهل أخطاء SSL (مفيد مع البروكسي)
        }
        
        if config.PROXY_ENABLED and config.PROXY_URL:
            # تحويل URL البروكسي إلى تنسيق Playwright
            from urllib.parse import urlparse
            parsed = urlparse(config.PROXY_URL)
            context_options['proxy'] = {
                'server': f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                'username': parsed.username,
                'password': parsed.password
            }
            print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
        
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        # محاولة تسجيل الدخول أولاً
        cookies_loaded = False
        if cookies:
            try:
                context.add_cookies(cookies)
                print("✅ تم تطبيق الكوكيز المحفوظة")
                cookies_loaded = True
            except Exception as e:
                print(f"⚠️ خطأ في تطبيق الكوكيز: {e}")
        
        # التحقق من صحة الكوكيز أو تسجيل الدخول
        print("🔍 التحقق من حالة تسجيل الدخول...")
        page.goto(config.BASE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        # التحقق من وجود زر تسجيل الدخول (يعني غير مسجل دخول)
        login_button = page.query_selector('a[href*="login"], button:has-text("تسجيل دخول"), button:has-text("Login")')
        
        if login_button:
            print("⚠️ يبدو أنك غير مسجل دخول. جاري تسجيل الدخول...")
            login_success = login_with_playwright(page, context, config.EMAIL, config.PASSWORD)
            if not login_success:
                print("❌ فشل تسجيل الدخول. يرجى التحقق من بيانات الدخول.")
                browser.close()
                return
        else:
            print("✅ يبدو أنك مسجل دخول بالفعل")
        
        # اعتراض network responses لالتقاط URLs الفيديو
        def capture_video(response):
            url = response.url
            
            # البحث عن manifest URLs (HLS streams)
            if ('manifest.prod.boltdns.net' in url or 
                'manifest' in url.lower()) and '.m3u8' in url:
                
                # محاولة الحصول على اسم الدرس
                try:
                    # البحث عن عنصر نشط في القائمة
                    active_selectors = [
                        '.active',
                        '[class*="active"]',
                        '[aria-selected="true"]',
                        '[class*="selected"]',
                        'li.active',
                        '.lesson-item.active',
                        '.chapter-item.active'
                    ]
                    
                    name = None
                    for selector in active_selectors:
                        try:
                            active = page.query_selector(selector)
                            if active:
                                name = active.inner_text().strip()
                                if name and len(name) < 200:
                                    break
                        except:
                            continue
                    
                    # إذا لم نجد عنصر نشط، نبحث في العنوان
                    if not name or len(name) < 3:
                        try:
                            title_elem = page.query_selector('h1, h2, .title, [class*="title"]')
                            if title_elem:
                                name = title_elem.inner_text().strip()[:100]
                        except:
                            pass
                    
                    # إذا لم نجد اسماً، نستخدم رقم تسلسلي
                    if not name or len(name) < 3:
                        name = f"video_{len(video_urls)+1}"
                    
                    # تنظيف الاسم
                    name = sanitize_filename(name)
                    
                    # التحقق من عدم تكرار URL
                    if url not in video_urls.values():
                        video_urls[name] = url
                        video_data.append({
                            'name': name,
                            'url': url,
                            'index': len(video_data) + 1
                        })
                        print(f"✅ تم التقاط فيديو {len(video_urls)}: {name[:50]}")
                        
                except Exception as e:
                    # إذا فشل استخراج الاسم، نستخدم رقم تسلسلي
                    if url not in video_urls.values():
                        name = f"video_{len(video_urls)+1}"
                        video_urls[name] = url
                        video_data.append({
                            'name': name,
                            'url': url,
                            'index': len(video_data) + 1
                        })
                        print(f"✅ تم التقاط فيديو {len(video_urls)}: {name}")
        
        page.on("response", capture_video)
        
        # تحميل صفحة الكورس
        print("📚 جاري تحميل صفحة الكورس...")
        try:
            page.goto(course_url, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            print("✅ تم تحميل الصفحة")
        except Exception as e:
            print(f"⚠️ تحذير في تحميل الصفحة: {e}")
            page.goto(course_url, timeout=60000)
            time.sleep(5)
        
        # البحث عن عناصر الدروس
        print("\n🔍 البحث عن عناصر الدروس...")
        time.sleep(2)
        
        # محاولة عدة selectors للعثور على عناصر الدروس
        lesson_selectors = [
            'li[class*="lesson"]',
            'li[class*="chapter"]',
            '[class*="lesson-item"]',
            '[class*="chapter-item"]',
            '[role="listitem"]',
            'button[class*="lesson"]',
            'a[href*="lesson"]',
            '.course-content li',
            '.lessons-list li',
            '.chapters-list li'
        ]
        
        lessons = []
        for selector in lesson_selectors:
            try:
                found = page.query_selector_all(selector)
                if found:
                    lessons = found
                    print(f"✅ تم العثور على {len(lessons)} عنصر باستخدام: {selector}")
                    break
            except:
                continue
        
        if not lessons:
            # محاولة البحث في جميع العناصر القابلة للنقر
            print("🔍 البحث في جميع العناصر القابلة للنقر...")
            all_clickable = page.query_selector_all('li, button, a, [role="button"]')
            lessons = []
            for el in all_clickable:
                try:
                    text = el.inner_text()
                    if text and len(text) < 200 and len(text) > 3:
                        # تصفية العناصر التي تبدو كدروس
                        if any(keyword in text.lower() for keyword in ['lesson', 'chapter', 'درس', 'مقدمة', 'intro']):
                            lessons.append(el)
                except:
                    pass
        
        print(f"📋 تم العثور على {len(lessons)} درس محتمل\n")
        
        if not lessons:
            print("⚠️ لم يتم العثور على دروس! سيتم محاولة النقر على العناصر الموجودة...")
            # محاولة النقر على أي عناصر قابلة للنقر
            all_elements = page.query_selector_all('li, button, a')
            lessons = all_elements[:50]  # حد أقصى 50 عنصر
        
        # النقر على كل درس
        print("👆 بدء النقر على الدروس...\n")
        for i, lesson in enumerate(lessons, 1):
            try:
                # إعادة الاستعلام لتجنب stale elements
                if i > 1:
                    lessons = page.query_selector_all(lesson_selectors[0] if lesson_selectors else 'li')
                    if i-1 < len(lessons):
                        lesson = lessons[i-1]
                
                # الحصول على اسم الدرس قبل النقر
                try:
                    lesson_name = lesson.inner_text().strip()[:100]
                except:
                    lesson_name = f"Lesson_{i}"
                
                # التمرير إلى العنصر
                lesson.scroll_into_view_if_needed()
                time.sleep(0.5)
                
                # النقر
                lesson.click()
                print(f"👆 تم النقر على الدرس {i}/{len(lessons)}: {lesson_name[:50]}")
                
                # انتظار تحميل الفيديو
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ خطأ في النقر على الدرس {i}: {e}")
                continue
        
        # انتظار إضافي لالتقاط أي URLs متأخرة
        print("\n⏳ انتظار لالتقاط أي URLs متأخرة...")
        time.sleep(5)
        
        browser.close()
    
    print(f"\n{'='*60}")
    print(f"🎬 إجمالي الفيديوهات الملتقطة: {len(video_urls)}")
    print(f"{'='*60}\n")
    
    if not video_urls:
        print("❌ لم يتم التقاط أي فيديوهات!")
        print("💡 نصائح:")
        print("   - تأكد من أن الكوكيز صحيحة")
        print("   - تأكد من أن الكورس متاح")
        print("   - جرب تشغيل السكريبت مع headless=False لرؤية ما يحدث")
        return
    
    # حفظ URLs في ملف JSON
    urls_file = output_path / "video_urls.json"
    with open(urls_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, indent=2, ensure_ascii=False)
    print(f"💾 تم حفظ URLs في: {urls_file}")
    
    # حفظ URLs في ملف نصي
    urls_txt_file = output_path / "urls.txt"
    with open(urls_txt_file, "w", encoding="utf-8") as f:
        for item in video_data:
            f.write(f"{item['name']}\n{item['url']}\n\n")
    print(f"💾 تم حفظ URLs في: {urls_txt_file}")
    
    # تحميل جميع الفيديوهات باستخدام ffmpeg
    print("\n⬇️ بدء تحميل الفيديوهات...\n")
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for item in video_data:
        name = item['name']
        url = item['url']
        index = item['index']
        
        safe_name = sanitize_filename(name)
        output_file = output_path / f"{index:02d}_{safe_name}.mp4"
        
        if output_file.exists() and output_file.stat().st_size > 1000:
            print(f"⏭️ تخطي {index}/{len(video_data)}: {name[:50]} (موجود بالفعل)")
            skipped += 1
            continue
        
        print(f"⬇️ تحميل {index}/{len(video_data)}: {name[:50]}...")
        
        try:
            # استخدام ffmpeg لتحميل HLS stream
            cmd = [
                "ffmpeg",
                "-i", url,
                "-c", "copy",  # بدون إعادة ترميز (أسرع)
                "-bsf:a", "aac_adtstoasc",
                "-y",  # الكتابة فوق الملف الموجود
                str(output_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 60 دقيقة كحد أقصى لكل فيديو
            )
            
            if result.returncode == 0 and output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"✅ تم: {output_file.name} ({size_mb:.2f} MB)")
                downloaded += 1
            else:
                print(f"❌ فشل التحميل: {result.stderr[:200] if result.stderr else 'خطأ غير معروف'}")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ انتهت مهلة التحميل: {name[:50]}")
            failed += 1
        except Exception as e:
            print(f"❌ خطأ: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 انتهى التحميل!")
    print(f"{'='*60}")
    print(f"✅ تم التحميل: {downloaded}")
    print(f"⏭️ تم التخطي: {skipped}")
    print(f"❌ فشل: {failed}")
    print(f"💾 الملفات محفوظة في: {output_path.absolute()}")
    print()


if __name__ == "__main__":
    # مثال على الاستخدام
    course_url = "https://yanfaa.com/us/single/learning_english_level_one"
    output_folder = "output/learning_english_level_one/videos"
    
    # يمكنك تغيير هذه القيم
    # course_url = "https://yanfaa.com/us/single/Learning_German_Level_1"
    # output_folder = "german_course"
    
    full_auto_download(
        course_url=course_url,
        output_folder=output_folder,
        headless=False  # False لعرض المتصفح، True لإخفائه
    )

