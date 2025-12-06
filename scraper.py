"""
منطق الكشط الشامل لموقع Yanfaa
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Optional, List, Set
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from auth import YanfaaAuth
import config

class YanfaaScraper:
    """كاشط شامل لموقع Yanfaa"""
    
    def __init__(self, auth: YanfaaAuth):
        self.auth = auth
        self.crawler: Optional[AsyncWebCrawler] = None
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.base_domain = urlparse(config.BASE_URL).netloc
    
    def _is_valid_url(self, url: str) -> bool:
        """التحقق من أن الرابط صالح للكشط"""
        try:
            parsed = urlparse(url)
            # التحقق من أن الرابط ينتمي لنفس الدومين
            if parsed.netloc and parsed.netloc != self.base_domain:
                return False
            # تجنب الملفات والموارد غير المهمة
            if any(url.lower().endswith(ext) for ext in ['.pdf', '.zip', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.ico']):
                return False
            # تجنب الروابط الخاصة (logout, etc.)
            if any(excluded in url.lower() for excluded in ['/logout', '/exit', 'javascript:', 'mailto:', 'tel:']):
                return False
            return True
        except:
            return False
    
    async def __aenter__(self):
        """إعداد الكاشط"""
        # إعداد البروكسي إذا كان مفعلاً
        proxy_server = None
        if config.PROXY_ENABLED and config.PROXY_URL:
            # تحويل رابط البروكسي إلى تنسيق مناسب لـ Playwright
            # تنسيق: http://username:password@host:port
            proxy_server = config.PROXY_URL
            print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
        
        # إعداد proxy_config إذا كان البروكسي مفعلاً
        proxy_config = None
        if proxy_server:
            # تحويل رابط البروكسي إلى تنسيق proxy_config لـ Playwright
            from urllib.parse import urlparse
            parsed = urlparse(proxy_server)
            # تنسيق Playwright: server فقط بدون username/password في proxy_config
            # username/password يتم تمريرها في URL
            proxy_config = proxy_server  # Playwright يقبل URL مباشرة
        
        browser_config = BrowserConfig(
            headless=config.HEADLESS,
            verbose=True,
            proxy_config=proxy_config
        )
        
        self.crawler = AsyncWebCrawler(config=browser_config)
        await self.crawler.__aenter__()
        
        # تطبيق الكوكيز المحفوظة
        cookies_list = self.auth.load_cookies_for_crawler()
        if cookies_list:
            print(f"🍪 تطبيق {len(cookies_list)} كوكيز محفوظة...")
            try:
                # تطبيق الكوكيز على المتصفح
                base_url = config.BASE_URL
                for cookie in cookies_list:
                    await self.crawler.cookie_manager.add_cookie(
                        url=base_url,
                        name=cookie['name'],
                        value=cookie['value'],
                        domain=cookie.get('domain', '.yanfaa.com'),
                        path=cookie.get('path', '/'),
                        secure=cookie.get('secure', False)
                    )
                print("✅ تم تطبيق الكوكيز بنجاح")
            except Exception as e:
                print(f"⚠️  تحذير: لم يتم تطبيق بعض الكوكيز: {str(e)}")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """إغلاق الكاشط"""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape_page(self, url: str, use_cookies: bool = True) -> Dict:
        """
        كشط صفحة معينة
        """
        if url in self.visited_urls:
            return {"success": False, "url": url, "error": "تم كشط هذه الصفحة مسبقاً"}
        
        if not self._is_valid_url(url):
            return {"success": False, "url": url, "error": "رابط غير صالح للكشط"}
        
        try:
            print(f"🔍 جاري كشط: {url}")
            
            # إعداد الكوكيز
            run_config = CrawlerRunConfig(
                wait_for="domcontentloaded",  # استخدام 'domcontentloaded' أسرع من 'load'
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=10,
                page_timeout=60000  # 60 ثانية
            )
            
            # تطبيق الكوكيز قبل الكشط
            cookies_list = self.auth.load_cookies_for_crawler()
            if cookies_list and use_cookies:
                try:
                    for cookie in cookies_list:
                        await self.crawler.cookie_manager.add_cookie(
                            url=url,
                            name=cookie['name'],
                            value=cookie['value'],
                            domain=cookie.get('domain', '.yanfaa.com'),
                            path=cookie.get('path', '/'),
                            secure=cookie.get('secure', False)
                        )
                except Exception as e:
                    print(f"⚠️  تحذير عند تطبيق الكوكيز: {str(e)}")
            
            # تنفيذ الكشط
            result = await self.crawler.arun(
                url=url,
                config=run_config
            )
            
            if result.success:
                # استخراج البيانات
                page_data = {
                    "success": True,
                    "url": url,
                    "final_url": result.metadata.get("final_url", url),
                    "title": result.metadata.get("title", ""),
                    "html": result.html,
                    "markdown": result.markdown,
                    "links": result.links or [],
                    "images": result.images or [],
                    "media": result.media or [],
                    "metadata": {
                        "description": result.metadata.get("description", ""),
                        "keywords": result.metadata.get("keywords", ""),
                        "author": result.metadata.get("author", ""),
                        "language": result.metadata.get("language", ""),
                    }
                }
                
                # إضافة للقائمة الزارعة
                self.visited_urls.add(url)
                self.scraped_data.append(page_data)
                
                # حفظ الصفحة في ملف منفصل
                await self._save_page(page_data)
                
                print(f"✅ تم كشط الصفحة بنجاح: {url}")
                return page_data
            else:
                error_data = {
                    "success": False,
                    "url": url,
                    "error": result.error_message
                }
                print(f"❌ فشل كشط الصفحة: {url} - {result.error_message}")
                return error_data
                
        except Exception as e:
            error_data = {
                "success": False,
                "url": url,
                "error": str(e)
            }
            print(f"❌ خطأ في كشط الصفحة: {url} - {str(e)}")
            return error_data
    
    async def _save_page(self, page_data: Dict):
        """حفظ صفحة في ملف منفصل"""
        try:
            # إنشاء اسم ملف آمن من URL
            url_path = urlparse(page_data['url']).path
            if not url_path or url_path == '/':
                filename = 'index'
            else:
                filename = url_path.replace('/', '_').replace('\\', '_').strip('_')
                if not filename:
                    filename = 'index'
            
            # حفظ HTML
            html_file = config.PAGES_DIR / f"{filename}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(page_data['html'])
            
            # حفظ Markdown
            if page_data.get('markdown'):
                md_file = config.PAGES_DIR / f"{filename}.md"
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(page_data['markdown'])
            
        except Exception as e:
            print(f"⚠️  خطأ في حفظ صفحة {page_data.get('url', '')}: {str(e)}")
    
    async def scrape_site(self, start_url: str = None, max_pages: int = None) -> List[Dict]:
        """
        كشط تلقائي لجميع الصفحات المتاحة
        """
        start_url = start_url or config.BASE_URL
        max_pages = max_pages or config.MAX_PAGES_TO_SCRAPE
        
        print(f"🚀 بدء الكشط الشامل من: {start_url}")
        print(f"📊 الحد الأقصى للصفحات: {max_pages}")
        
        # قائمة انتظار للروابط
        url_queue = [start_url]
        
        while url_queue and len(self.visited_urls) < max_pages:
            current_url = url_queue.pop(0)
            
            # تجنب التكرار
            if current_url in self.visited_urls:
                continue
            
            # كشط الصفحة الحالية
            page_data = await self.scrape_page(current_url)
            
            if page_data.get("success"):
                # استخراج الروابط الداخلية
                links = page_data.get("links", [])
                for link in links:
                    if isinstance(link, dict):
                        link_url = link.get("href") or link.get("url", "")
                    elif isinstance(link, str):
                        link_url = link
                    else:
                        continue
                    
                    # تحويل الرابط النسبي إلى مطلق
                    if link_url:
                        absolute_url = urljoin(config.BASE_URL, link_url)
                        
                        # إزالة التجزئة (#) من الروابط
                        absolute_url = absolute_url.split('#')[0]
                        
                        # التحقق من صحة الرابط وإضافته للقائمة
                        if (self._is_valid_url(absolute_url) and 
                            absolute_url not in self.visited_urls and 
                            absolute_url not in url_queue):
                            url_queue.append(absolute_url)
                
                # انتظار بين الطلبات
                await asyncio.sleep(config.DELAY_BETWEEN_REQUESTS)
            
            # تحديث التقدم
            if len(self.visited_urls) % 10 == 0:
                print(f"📈 التقدم: {len(self.visited_urls)} صفحة مكشوطة")
        
        print(f"✅ اكتمل الكشط: {len(self.visited_urls)} صفحة مكشوطة")
        return self.scraped_data
    
    async def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """كشط عدة صفحات محددّة"""
        results = []
        for url in urls:
            result = await self.scrape_page(url)
            results.append(result)
            await asyncio.sleep(config.DELAY_BETWEEN_REQUESTS)
        return results
    
    def save_results(self, output_file: str = None):
        """حفظ جميع النتائج في ملف JSON"""
        output_file = output_file or config.SCRAPED_DATA_FILE
        
        try:
            results_data = {
                "total_pages": len(self.scraped_data),
                "successful_pages": len([d for d in self.scraped_data if d.get("success")]),
                "failed_pages": len([d for d in self.scraped_data if not d.get("success")]),
                "visited_urls": list(self.visited_urls),
                "pages": self.scraped_data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ تم حفظ النتائج في {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ خطأ في حفظ النتائج: {str(e)}")
            return None


