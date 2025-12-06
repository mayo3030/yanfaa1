"""
اختبار البروكسي مع Playwright مباشرة
"""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig
import config

async def test_playwright_proxy():
    """اختبار البروكسي مع Playwright"""
    print("=" * 60)
    print("🔍 اختبار البروكسي مع Playwright")
    print("=" * 60)
    print()
    
    if not config.PROXY_ENABLED:
        print("⚠️ البروكسي معطل")
        return False
    
    print(f"🌐 استخدام البروكسي: {config.PROXY_HOST}:{config.PROXY_PORT}")
    print(f"   URL: {config.PROXY_URL[:50]}...")
    print()
    
    try:
        browser_config = BrowserConfig(
            headless=False,  # عرض المتصفح لرؤية ما يحدث
            verbose=True,
            proxy_config=config.PROXY_URL
        )
        
        print("🔍 جاري الاتصال...")
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("✅ تم الاتصال بنجاح")
            print("🔍 جاري فتح صفحة اختبار...")
            
            # اختبار مع Yanfaa
            result = await crawler.arun(
                url=config.BASE_URL,
                word_count_threshold=10
            )
            
            if result.success:
                print("✅ نجح الاتصال!")
                print(f"   العنوان: {result.metadata.get('final_url', 'N/A')}")
                print(f"   HTML length: {len(result.html) if result.html else 0}")
                if result.markdown:
                    print(f"   Markdown preview: {result.markdown[:200]}")
                return True
            else:
                print(f"❌ فشل الاتصال: {result.error_message}")
                return False
                
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_playwright_proxy())

