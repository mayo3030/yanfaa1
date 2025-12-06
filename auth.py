"""
إدارة المصادقة والجلسات لموقع Yanfaa
"""
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode
import config

class YanfaaAuth:
    """إدارة المصادقة والجلسات لموقع Yanfaa"""
    
    def __init__(self, email: str = None, password: str = None, cookies_file: str = None):
        self.email = email or config.EMAIL
        self.password = password or config.PASSWORD
        self.cookies_file = Path(cookies_file) if cookies_file else config.COOKIES_FILE
        self.session_cookies: Optional[Dict] = None
    
    async def login(self) -> bool:
        """
        تسجيل الدخول وحفظ الجلسة والكوكيز
        """
        login_url = config.LOGIN_URL
        
        # إعداد البروكسي إذا كان مفعلاً
        proxy_config = None
        if config.PROXY_ENABLED and config.PROXY_URL:
            proxy_config = config.PROXY_URL  # Playwright يقبل URL مباشرة
            print(f"🌐 استخدام البروكسي لتسجيل الدخول: {config.PROXY_HOST}:{config.PROXY_PORT}")
        
        browser_config = BrowserConfig(
            headless=config.HEADLESS,
            verbose=True,
            proxy_config=proxy_config
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            try:
                print("🔐 جاري تسجيل الدخول...")
                
                # تنفيذ تسجيل الدخول
                # بناء JavaScript code مع escape للقيم
                email_escaped = self.email.replace("'", "\\'").replace('"', '\\"')
                password_escaped = self.password.replace("'", "\\'").replace('"', '\\"')
                
                js_code = f"""
                    // انتظار تحميل الصفحة
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    
                    // محاولة العثور على حقول تسجيل الدخول
                    let emailInput = document.querySelector('input[type="email"]') || 
                                    document.querySelector('input[name="email"]') || 
                                    document.querySelector('input[id*="email" i]') ||
                                    document.querySelector('input[placeholder*="بريد" i]') ||
                                    document.querySelector('input[placeholder*="email" i]');
                    
                    let passwordInput = document.querySelector('input[type="password"]') || 
                                       document.querySelector('input[name="password"]') || 
                                       document.querySelector('input[id*="password" i]') ||
                                       document.querySelector('input[placeholder*="كلمة" i]');
                    
                    let submitButton = document.querySelector('button[type="submit"]') || 
                                      document.querySelector('input[type="submit"]') || 
                                      document.querySelector('button[name*="login" i]') ||
                                      document.querySelector('button:has-text("تسجيل دخول")') ||
                                      document.querySelector('button.btn-primary') ||
                                      document.querySelector('form button');
                    
                    if (emailInput && passwordInput) {{
                        // إدخال البريد الإلكتروني
                        emailInput.value = '{self.email}';
                        emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        emailInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        // إدخال كلمة المرور
                        passwordInput.value = '{self.password}';
                        passwordInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        passwordInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        // تفعيل checkbox "تذكرني" إذا كان موجوداً
                        let rememberMe = document.querySelector('input[type="checkbox"]');
                        if (rememberMe && !rememberMe.checked) {{
                            rememberMe.click();
                        }}
                        
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                        // الضغط على زر تسجيل الدخول
                        if (submitButton) {{
                            submitButton.click();
                            // انتظار التوجيه أو تحميل الصفحة التالية
                            await new Promise(resolve => setTimeout(resolve, 5000));
                        }} else {{
                            // محاولة إرسال النموذج مباشرة
                            let form = emailInput.closest('form');
                            if (form) {{
                                form.submit();
                                await new Promise(resolve => setTimeout(resolve, 5000));
                            }}
                        }}
                    }} else {{
                        console.log('لم يتم العثور على حقول تسجيل الدخول');
                        console.log('Email input found:', !!emailInput);
                        console.log('Password input found:', !!passwordInput);
                    }}
                    
                    const cookieData = {{
                        cookieStr: document.cookie,
                        url: window.location.href,
                        title: document.title
                    }};
                    
                    // حفظ الكوكيز في window للوصول إليها لاحقاً
                    window._yanfaa_cookies = document.cookie;
                    
                    return cookieData;
                    """
                
                result = await crawler.arun(
                    url=login_url,
                    word_count_threshold=10,
                    cache_mode=CacheMode.BYPASS,
                    js_code=js_code,
                    wait_for="load"  # استخدام 'load' بدلاً من 'networkidle' لتقليل وقت الانتظار
                )
                
                if result.success:
                    # الحصول على الكوكيز من المتصفح
                    try:
                        cookies = []
                        # محاولة الحصول على الكوكيز من Playwright مباشرة
                        try:
                            # الوصول إلى Playwright context من خلال crawler
                            if hasattr(crawler, '_playwright_browser') and crawler._playwright_browser:
                                contexts = crawler._playwright_browser.contexts
                                if contexts:
                                    cookies = await contexts[0].cookies()
                        except AttributeError:
                            # محاولة طريقة أخرى
                            try:
                                if hasattr(crawler, 'browser') and crawler.browser:
                                    contexts = crawler.browser.contexts
                                    if contexts:
                                        cookies = await contexts[0].cookies()
                            except Exception:
                                pass
                        except Exception as e:
                            print(f"⚠️  تحذير: لم يتم الحصول على الكوكيز من Playwright: {str(e)}")
                        
                        # إذا لم نحصل على الكوكيز من Playwright، نحاول من JavaScript
                        if not cookies:
                            try:
                                # الحصول على الكوكيز من JavaScript
                                cookie_js_result = await crawler.arun(
                                    url=result.metadata.get('final_url', login_url),
                                    js_code="return window._yanfaa_cookies || document.cookie;",
                                    word_count_threshold=1,
                                    wait_for="load"
                                )
                                if cookie_js_result.success:
                                    # محاولة استخراج الكوكيز من extracted_content أو html
                                    cookie_string = None
                                    if hasattr(cookie_js_result, 'extracted_content') and cookie_js_result.extracted_content:
                                        cookie_string = cookie_js_result.extracted_content
                                    elif hasattr(cookie_js_result, 'html') and cookie_js_result.html:
                                        # البحث عن الكوكيز في HTML
                                        import re
                                        match = re.search(r'window\._yanfaa_cookies\s*=\s*["\']([^"\']+)["\']', cookie_js_result.html)
                                        if match:
                                            cookie_string = match.group(1)
                                    
                                    if cookie_string:
                                        # تحويل cookie string إلى dict
                                        cookies_dict = {}
                                        for cookie in cookie_string.split(';'):
                                            cookie = cookie.strip()
                                            if '=' in cookie:
                                                name, value = cookie.split('=', 1)
                                                cookies_dict[name] = value
                                        cookies = cookies_dict
                            except Exception as e:
                                print(f"⚠️  تحذير: لم يتم الحصول على الكوكيز من JavaScript: {str(e)}")
                        
                        # حفظ الكوكيز
                        if cookies:
                            # تحويل إلى تنسيق موحد
                            if isinstance(cookies, list):
                                # تنسيق Playwright cookies
                                cookies_dict = {}
                                for cookie in cookies:
                                    if cookie.get('name'):
                                        cookies_dict[cookie['name']] = {
                                            'value': cookie.get('value', ''),
                                            'domain': cookie.get('domain', '.yanfaa.com'),
                                            'path': cookie.get('path', '/'),
                                            'secure': cookie.get('secure', False),
                                            'expiration': cookie.get('expires', 0) if cookie.get('expires') else 0
                                        }
                                cookies = cookies_dict
                            
                            # حفظ الكوكيز في متغير المثال
                            self.session_cookies = cookies
                            
                            # حفظ الكوكيز في ملف
                            self.save_cookies(cookies)
                            
                            print("✅ تم تسجيل الدخول بنجاح وحفظ الكوكيز")
                            print(f"   🍪 تم حفظ {len(cookies)} كوكيز")
                            print(f"📍 العنوان الحالي: {result.metadata.get('final_url', login_url)}")
                            
                            return True
                        else:
                            print("⚠️  تم تسجيل الدخول ولكن لم يتم العثور على الكوكيز")
                            print("   سيتم المحاولة بدون حفظ الكوكيز")
                            return True
                            
                    except Exception as cookie_error:
                        print(f"⚠️  تم تسجيل الدخول ولكن حدث خطأ في حفظ الكوكيز: {{str(cookie_error)}}")
                        import traceback
                        traceback.print_exc()
                        return True
                else:
                    print(f"❌ فشل تسجيل الدخول: {result.error_message}")
                    if hasattr(result, 'screenshot') and result.screenshot:
                        screenshot_path = config.OUTPUT_DIR / "login_error.png"
                        with open(screenshot_path, 'wb') as f:
                            f.write(result.screenshot)
                        print(f"📸 تم حفظ لقطة شاشة للخطأ في: {screenshot_path}")
                    return False
                    
            except Exception as e:
                print(f"❌ خطأ في تسجيل الدخول: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
    
    def save_cookies(self, cookies: Dict):
        """حفظ الكوكيز في ملف JSON"""
        try:
            # تحويل الكوكيز إلى تنسيق قابل للتخزين
            cookies_to_save = {}
            
            if isinstance(cookies, dict):
                for key, value in cookies.items():
                    if isinstance(value, dict):
                        # إذا كانت الكوكيز في تنسيق playwright
                        cookies_to_save[key] = value
                    else:
                        cookies_to_save[key] = value
            elif isinstance(cookies, list):
                # إذا كانت قائمة من الكوكيز
                for cookie in cookies:
                    if isinstance(cookie, dict) and 'name' in cookie:
                        cookies_to_save[cookie['name']] = cookie['value']
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_to_save, f, indent=2, ensure_ascii=False)
            print(f"✅ تم حفظ الكوكيز في {self.cookies_file}")
        except Exception as e:
            print(f"❌ خطأ في حفظ الكوكيز: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_cookies(self) -> Optional[Dict]:
        """تحميل الكوكيز من ملف JSON"""
        try:
            if self.cookies_file.exists():
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    self.session_cookies = json.load(f)
                    print(f"✅ تم تحميل الكوكيز من {self.cookies_file}")
                    return self.session_cookies
            else:
                print(f"ℹ️  ملف الكوكيز غير موجود: {self.cookies_file}")
                return None
        except Exception as e:
            print(f"❌ خطأ في تحميل الكوكيز: {str(e)}")
            return None
    
    def load_cookies_for_crawler(self) -> Optional[list]:
        """تحميل الكوكيز بتنسيق مناسب لـ Crawl4AI"""
        cookies_dict = self.load_cookies()
        if not cookies_dict:
            return None
        
        cookies_list = []
        for name, value in cookies_dict.items():
            if isinstance(value, dict):
                # إذا كانت الكوكيز في تنسيق متقدم
                cookie = {
                    'name': value.get('name', name),
                    'value': value.get('value', str(value)),
                    'domain': value.get('domain', '.yanfaa.com'),
                    'path': value.get('path', '/'),
                    'secure': value.get('secure', False),
                }
                if value.get('expiration'):
                    cookie['expires'] = value.get('expiration')
            else:
                # تنسيق بسيط
                cookie = {
                    'name': name,
                    'value': str(value),
                    'domain': '.yanfaa.com',
                    'path': '/',
                    'secure': False
                }
            cookies_list.append(cookie)
        
        return cookies_list
    
    def get_cookies(self) -> Optional[Dict]:
        """الحصول على الكوكيز الحالية"""
        return self.session_cookies
    
    def is_logged_in(self) -> bool:
        """التحقق من وجود جلسة محفوظة"""
        cookies = self.load_cookies()
        return cookies is not None and len(cookies) > 0
    
    async def verify_session(self) -> bool:
        """التحقق من صحة الجلسة باستخدام الكوكيز"""
        if not self.is_logged_in():
            return False
        
        try:
            # إعداد البروكسي إذا كان مفعلاً
            proxy_config = None
            if config.PROXY_ENABLED and config.PROXY_URL:
                proxy_config = config.PROXY_URL  # Playwright يقبل URL مباشرة
            
            browser_config = BrowserConfig(
                headless=True,
                verbose=False,
                proxy_config=proxy_config
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # تطبيق الكوكيز
                cookies_list = self.load_cookies_for_crawler()
                if cookies_list:
                    base_url = config.BASE_URL
                    for cookie in cookies_list:
                        await crawler.cookie_manager.add_cookie(
                            url=base_url,
                            name=cookie['name'],
                            value=cookie['value'],
                            domain=cookie.get('domain', '.yanfaa.com'),
                            path=cookie.get('path', '/'),
                            secure=cookie.get('secure', False)
                        )
                
                # محاولة الوصول إلى صفحة محمية
                result = await crawler.arun(
                    url=config.BASE_URL,
                    word_count_threshold=10,
                    wait_for="networkidle"
                )
                
                if result.success:
                    # التحقق من أن الصفحة ليست صفحة تسجيل دخول
                    final_url = result.metadata.get('final_url', '')
                    if 'login' not in final_url.lower() and result.html:
                        return True
                
                return False
        except Exception as e:
            print(f"⚠️  خطأ في التحقق من الجلسة: {str(e)}")
            return False


