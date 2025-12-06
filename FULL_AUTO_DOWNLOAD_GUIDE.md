# 🚀 دليل التحميل التلقائي الكامل

## 📋 نظرة عامة

هذا السكريبت يقوم بـ **تحميل تلقائي كامل** لجميع فيديوهات الكورس:

- ✅ يفتح كل درس تلقائياً
- ✅ يجمع URLs الفيديو من network requests
- ✅ يحفظ URLs في ملف
- ✅ يحمل جميع الفيديوهات باستخدام ffmpeg
- ✅ يتخطى الفيديوهات المحملة مسبقاً

## 🔧 المتطلبات

### 1. تثبيت Python Libraries

```bash
pip install playwright
playwright install chromium
```

### 2. تثبيت FFmpeg

#### Windows (مع Chocolatey):
```bash
choco install ffmpeg
```

#### Windows (بدون Chocolatey):
1. اذهب إلى: https://ffmpeg.org/download.html
2. حمّل النسخة المناسبة
3. أضف `ffmpeg` إلى PATH

#### Linux:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

### 3. ملف الكوكيز

تأكد من وجود ملف `cookies_yanfaa_account.json` في المجلد الرئيسي.

## 🚀 الاستخدام

### الطريقة البسيطة:

```python
from full_auto_download import full_auto_download

full_auto_download(
    course_url="https://yanfaa.com/us/single/learning_english_level_one",
    output_folder="output/learning_english_level_one/videos",
    headless=False  # False لعرض المتصفح
)
```

### أو تشغيل الملف مباشرة:

```bash
python full_auto_download.py
```

## ⚙️ الإعدادات

يمكنك تعديل الإعدادات في بداية الملف:

```python
course_url = "https://yanfaa.com/us/single/learning_english_level_one"
output_folder = "output/learning_english_level_one/videos"
headless = False  # True لإخفاء المتصفح
```

## 📁 الملفات الناتجة

بعد التشغيل، ستحصل على:

1. **`video_urls.json`**: ملف JSON يحتوي على جميع URLs مع الأسماء
2. **`urls.txt`**: ملف نصي بسيط يحتوي على URLs
3. **`01_video_name.mp4`**: الفيديوهات المحملة

## 🎯 المميزات

| الميزة | الوصف |
|--------|-------|
| 🤖 **Full Auto** | يفتح كل درس لوحده تلقائياً |
| 📡 **Intercepts URLs** | يمسك video URLs من network requests |
| 💾 **Saves List** | يحفظ كل URLs في ملف |
| ⬇️ **Auto Download** | يحمل كل الفيديوهات بـ ffmpeg |
| ⏭️ **Skip Existing** | يتخطى الفيديوهات الموجودة |

## 🔍 استكشاف الأخطاء

### المشكلة: لم يتم التقاط أي فيديوهات

**الحلول:**
1. تأكد من أن الكوكيز صحيحة وحديثة
2. شغّل السكريبت مع `headless=False` لرؤية ما يحدث
3. تأكد من أن الكورس متاح ومفتوح

### المشكلة: خطأ في ffmpeg

**الحلول:**
1. تأكد من تثبيت ffmpeg
2. تأكد من إضافة ffmpeg إلى PATH
3. اختبر ffmpeg يدوياً: `ffmpeg -version`

### المشكلة: فشل في النقر على الدروس

**الحلول:**
1. قد تحتاج لتعديل selectors في الكود
2. شغّل مع `headless=False` لرؤية المشكلة
3. زد وقت الانتظار بين النقرات

## 📝 ملاحظات

- السكريبت يستخدم **Playwright** لفتح المتصفح
- يستخدم **ffmpeg** لتحميل HLS streams
- يدعم **البروكسي** من ملف `config.py`
- يحفظ **التقدم** ويتخطى الفيديوهات المحملة

## 🎉 مثال على الإخراج

```
============================================================
🚀 بدء التحميل التلقائي الكامل
============================================================
📚 رابط الكورس: https://yanfaa.com/us/single/learning_english_level_one
💾 مجلد الحفظ: output/learning_english_level_one/videos

✅ تم تحميل 15 كوكيز
✅ تم تطبيق الكوكيز
📚 جاري تحميل صفحة الكورس...
✅ تم تحميل الصفحة

🔍 البحث عن عناصر الدروس...
✅ تم العثور على 29 عنصر باستخدام: li[class*="lesson"]

👆 بدء النقر على الدروس...

👆 تم النقر على الدرس 1/29: Lesson 1 - Introduction
✅ تم التقاط فيديو 1: Lesson_1_Introduction
👆 تم النقر على الدرس 2/29: Lesson 2 - Basics
✅ تم التقاط فيديو 2: Lesson_2_Basics
...

============================================================
🎬 إجمالي الفيديوهات الملتقطة: 29
============================================================

⬇️ بدء تحميل الفيديوهات...

⬇️ تحميل 1/29: Lesson_1_Introduction...
✅ تم: 01_Lesson_1_Introduction.mp4 (125.34 MB)
⬇️ تحميل 2/29: Lesson_2_Basics...
✅ تم: 02_Lesson_2_Basics.mp4 (98.76 MB)
...

============================================================
🎉 انتهى التحميل!
============================================================
✅ تم التحميل: 29
⏭️ تم التخطي: 0
❌ فشل: 0
💾 الملفات محفوظة في: C:\Users\...\output\learning_english_level_one\videos
```

## 🆘 الدعم

إذا واجهت أي مشاكل:
1. تحقق من ملف `config.py` للإعدادات
2. تأكد من تثبيت جميع المتطلبات
3. شغّل مع `headless=False` لرؤية ما يحدث



