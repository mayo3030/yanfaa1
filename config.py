"""
ملف الإعدادات المركزي لتطبيق كشط Yanfaa
"""
import os
from pathlib import Path

# بيانات تسجيل الدخول
EMAIL = "minasalama2019@gmail.com"
PASSWORD = "Adelafafy2020"

# مسارات الملفات
BASE_DIR = Path(__file__).parent
COOKIES_FILE = BASE_DIR / "cookies.json"
OUTPUT_DIR = BASE_DIR / "output"
PAGES_DIR = OUTPUT_DIR / "pages"
SCRAPED_DATA_FILE = OUTPUT_DIR / "scraped_data.json"

# إعدادات الكشط
LOGIN_URL = "https://yanfaa.com/us/login"
BASE_URL = "https://yanfaa.com"
HEADLESS = False  # False لعرض المتصفح، True للإخفاء
DELAY_BETWEEN_REQUESTS = 2  # ثواني الانتظار بين طلبات الكشط
MAX_PAGES_TO_SCRAPE = 1000  # الحد الأقصى لعدد الصفحات

# إعدادات المتصفح
BROWSER_CONFIG = {
    "headless": HEADLESS,
    "verbose": True,
}

# إعدادات البروكسي (BrightData)
PROXY_ENABLED = True  # تفعيل/تعطيل البروكسي
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335
PROXY_USERNAME = "brd-customer-hl_4e6b8d69-zone-yanfaaa"
PROXY_PASSWORD = "76roammwqt6k"

# بناء رابط البروكسي
PROXY_URL = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}" if PROXY_ENABLED else None

# إنشاء المجلدات المطلوبة
OUTPUT_DIR.mkdir(exist_ok=True)
PAGES_DIR.mkdir(exist_ok=True)



