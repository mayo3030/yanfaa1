"""
سكريبت لحفظ جلسة الكوكيز من المتصفح
"""
import asyncio
import sys
from auth import YanfaaAuth
import config

async def save_cookies_session():
    """حفظ جلسة الكوكيز"""
    print("=" * 60)
    print("🍪 حفظ جلسة الكوكيز")
    print("=" * 60)
    print()
    
    auth = YanfaaAuth()
    
    # التحقق من وجود الكوكيز المحفوظة
    cookies = auth.load_cookies()
    
    if cookies and auth.is_logged_in():
        print("✅ توجد جلسة محفوظة بالفعل")
        print(f"   🍪 عدد الكوكيز: {len(cookies)}")
        print(f"   📁 الملف: {auth.cookies_file}")
        print()
        
        response = input("هل تريد تحديث الجلسة؟ (y/n): ")
        if response.lower() != 'y':
            print("❌ تم الإلغاء")
            return False
    
    print("🔐 جاري تسجيل الدخول وحفظ الجلسة...")
    print(f"📧 البريد الإلكتروني: {config.EMAIL}")
    print()
    
    login_success = await auth.login()
    
    if login_success:
        # التحقق من حفظ الكوكيز
        saved_cookies = auth.load_cookies()
        if saved_cookies:
            print()
            print("=" * 60)
            print("✅ تم حفظ الجلسة بنجاح!")
            print("=" * 60)
            print(f"   🍪 عدد الكوكيز المحفوظة: {len(saved_cookies)}")
            print(f"   📁 الملف: {auth.cookies_file}")
            print()
            print("💡 يمكنك الآن استخدام هذه الجلسة في الكشط")
            return True
        else:
            print("⚠️  تم تسجيل الدخول ولكن لم يتم حفظ الكوكيز")
            return False
    else:
        print("❌ فشل تسجيل الدخول")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(save_cookies_session())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف العملية بواسطة المستخدم")
        sys.exit(0)



