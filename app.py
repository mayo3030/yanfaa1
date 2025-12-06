"""
التطبيق الرئيسي لكشط موقع Yanfaa
"""
import asyncio
import sys
from pathlib import Path
from auth import YanfaaAuth
from scraper import YanfaaScraper
import config

async def main():
    """الدالة الرئيسية للتطبيق"""
    
    print("=" * 60)
    print("🚀 تطبيق كشط موقع Yanfaa")
    print("=" * 60)
    print()
    
    # إنشاء كائن المصادقة
    auth = YanfaaAuth()
    
    # التحقق من وجود الكوكيز المحفوظة
    print("🔍 التحقق من وجود جلسة محفوظة...")
    cookies = auth.load_cookies()
    
    # إذا لم تكن هناك كوكيز محفوظة، قم بتسجيل الدخول
    if not cookies or not auth.is_logged_in():
        print("📝 لا توجد جلسة محفوظة، جاري تسجيل الدخول...")
        print(f"📧 البريد الإلكتروني: {config.EMAIL}")
        print()
        
        login_success = await auth.login()
        if not login_success:
            print("❌ فشل تسجيل الدخول. يرجى التحقق من البيانات وإعادة المحاولة.")
            print("💡 ملاحظة: قد تحتاج إلى حل reCAPTCHA يدوياً في المتصفح.")
            sys.exit(1)
        
        # إعادة تحميل الكوكيز بعد تسجيل الدخول
        cookies = auth.load_cookies()
    else:
        print("✅ تم تحميل الجلسة المحفوظة بنجاح")
        print(f"🍪 عدد الكوكيز المحفوظة: {len(cookies) if cookies else 0}")
    
    print()
    print("=" * 60)
    print("🌐 بدء عملية الكشط")
    print("=" * 60)
    print()
    
    # إنشاء الكاشط
    try:
        async with YanfaaScraper(auth) as scraper:
            # خيارات الكشط
            print("اختر طريقة الكشط:")
            print("1. كشط شامل لجميع الصفحات المتاحة (موصى به)")
            print("2. كشط صفحات محددة")
            
            # للتبسيط، سنستخدم الكشط الشامل بشكل افتراضي
            # يمكنك تعديل هذا لطلب إدخال من المستخدم
            choice = "1"  # يمكن تغيير هذا ليكون input()
            
            if choice == "1":
                # كشط شامل
                print("\n🚀 بدء الكشط الشامل...")
                results = await scraper.scrape_site(
                    start_url=config.BASE_URL,
                    max_pages=config.MAX_PAGES_TO_SCRAPE
                )
            else:
                # كشط صفحات محددة
                urls_to_scrape = [
                    config.BASE_URL,
                    config.LOGIN_URL,
                    # يمكن إضافة المزيد من الروابط هنا
                ]
                print(f"\n🔍 كشط {len(urls_to_scrape)} صفحة محددة...")
                results = await scraper.scrape_multiple_pages(urls_to_scrape)
            
            # حفظ النتائج
            print("\n" + "=" * 60)
            print("💾 حفظ النتائج")
            print("=" * 60)
            
            output_file = scraper.save_results()
            
            if output_file:
                # عرض ملخص
                successful = len([r for r in scraper.scraped_data if r.get("success")])
                failed = len([r for r in scraper.scraped_data if not r.get("success")])
                
                print(f"\n📊 ملخص النتائج:")
                print(f"   ✅ الصفحات المكشوطة بنجاح: {successful}")
                print(f"   ❌ الصفحات الفاشلة: {failed}")
                print(f"   📄 إجمالي الصفحات: {len(scraper.scraped_data)}")
                print(f"   🔗 الروابط الفريدة: {len(scraper.visited_urls)}")
                print()
                print(f"📁 ملف النتائج: {output_file}")
                print(f"📁 صفحات HTML/Markdown: {config.PAGES_DIR}")
                print()
                print("=" * 60)
                print("✅ اكتمل التطبيق بنجاح!")
                print("=" * 60)
            else:
                print("❌ فشل حفظ النتائج")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        print("💾 حفظ البيانات الحالية...")
        if 'scraper' in locals():
            scraper.save_results()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف التطبيق")
        sys.exit(0)





