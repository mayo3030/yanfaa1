"""
اختبار البروكسي
"""
import httpx
import config
from proxy_helper import get_httpx_client

def test_proxy():
    """اختبار البروكسي"""
    print("=" * 60)
    print("🔍 اختبار البروكسي BrightData")
    print("=" * 60)
    print()
    
    if not config.PROXY_ENABLED:
        print("⚠️ البروكسي معطل في الإعدادات")
        print("   قم بتفعيل PROXY_ENABLED = True في config.py")
        return False
    
    print(f"📋 معلومات البروكسي:")
    print(f"   Host: {config.PROXY_HOST}")
    print(f"   Port: {config.PROXY_PORT}")
    print(f"   Username: {config.PROXY_USERNAME[:20]}...")
    print()
    
    try:
        # اختبار البروكسي مع BrightData test endpoint
        print("🔍 اختبار الاتصال بالبروكسي...")
        client = get_httpx_client(timeout=30)
        
        test_url = "https://geo.brdtest.com/welcome.txt?product=resi&method=native"
        response = client.get(test_url)
        
        print(f"✅ حالة الاتصال: {response.status_code}")
        print(f"📄 النتيجة:")
        print(f"   {response.text[:300]}")
        print()
        
        # اختبار الوصول لـ Yanfaa
        print("🔍 اختبار الوصول لـ Yanfaa...")
        yanfaa_response = client.get(config.BASE_URL, timeout=30)
        print(f"✅ حالة Yanfaa: {yanfaa_response.status_code}")
        
        if yanfaa_response.status_code == 200:
            print(f"   العنوان: {yanfaa_response.url}")
            print(f"   حجم الصفحة: {len(yanfaa_response.text)} بايت")
            print()
            print("=" * 60)
            print("✅ البروكسي يعمل بشكل صحيح!")
            print("=" * 60)
            return True
        else:
            print(f"⚠️ تحذير: حالة غير متوقعة {yanfaa_response.status_code}")
            return False
            
    except httpx.ProxyError as e:
        print(f"❌ خطأ في الاتصال بالبروكسي: {str(e)}")
        print("   تحقق من:")
        print("   - بيانات البروكسي في config.py")
        print("   - اتصال الإنترنت")
        print("   - صلاحية بيانات BrightData")
        return False
    except httpx.TimeoutException:
        print(f"❌ انتهت مهلة الاتصال")
        print("   البروكسي قد يكون بطيئاً أو غير متاح")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    success = test_proxy()
    exit(0 if success else 1)



