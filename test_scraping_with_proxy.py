"""
اختبار الكشط باستخدام البروكسي
"""
import asyncio
import sys
from auth import YanfaaAuth
from scraper import YanfaaScraper
import config

async def test_scraping_with_proxy():
    """اختبار الكشط مع البروكسي"""
    print("=" * 60)
    print("🔍 اختبار الكشط باستخدام البروكسي")
    print("=" * 60)
    print()
    
    # التحقق من حالة البروكسي
    if not config.PROXY_ENABLED:
        print("⚠️ البروكسي معطل في الإعدادات")
        response = input("هل تريد تفعيل البروكسي؟ (y/n): ")
        if response.lower() == 'y':
            config.PROXY_ENABLED = True
            print("✅ تم تفعيل البروكسي")
        else:
            print("❌ سيتم المتابعة بدون بروكسي")
    
    print(f"🌐 حالة البروكسي: {'مفعّل ✅' if config.PROXY_ENABLED else 'معطّل ❌'}")
    if config.PROXY_ENABLED:
        print(f"   Host: {config.PROXY_HOST}:{config.PROXY_PORT}")
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
    else:
        print("✅ تم تحميل الجلسة المحفوظة بنجاح")
        print(f"🍪 عدد الكوكيز المحفوظة: {len(cookies) if cookies else 0}")
    
    print()
    print("=" * 60)
    print("🌐 بدء اختبار الكشط")
    print("=" * 60)
    print()
    
    # اختبار كشط صفحة واحدة
    try:
        async with YanfaaScraper(auth) as scraper:
            # كشط الصفحة الرئيسية
            test_url = config.BASE_URL
            print(f"🔍 جاري كشط: {test_url}")
            print()
            
            result = await scraper.scrape_page(test_url)
            
            if result.get("success"):
                print("✅ نجح الكشط!")
                print(f"   العنوان: {result.get('url')}")
                print(f"   العنوان النهائي: {result.get('final_url')}")
                print(f"   العنوان: {result.get('title', 'N/A')}")
                print(f"   عدد الروابط: {len(result.get('links', []))}")
                print(f"   عدد الصور: {len(result.get('images', []))}")
                print()
                print("=" * 60)
                print("✅ البروكسي يعمل بشكل صحيح مع الكشط!")
                print("=" * 60)
                return True
            else:
                print("❌ فشل الكشط")
                print(f"   الخطأ: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_scraping_with_proxy())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        sys.exit(0)



