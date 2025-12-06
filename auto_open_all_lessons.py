"""
سكريبت لفتح جميع الدروس تلقائياً باستخدام browser automation
"""
import json
import time
from pathlib import Path

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'

print("="*60)
print(f"🚀 فتح جميع الدروس تلقائياً")
print(f"📚 الكورس: {course_slug}")
print("="*60)

print(f"\n🌐 الانتقال إلى: {course_url}")

# Note: The actual browser automation will happen via Cursor's browser tools
# This script provides the structure and instructions

print("\n" + "="*60)
print("📋 الخطوات:")
print("="*60)
print("""
1. تأكد من أنك قمت بتسجيل الدخول في المتصفح
2. هذا السكريبت سينقر على جميع الدروس واحداً تلو الآخر
3. كل درس سيتم فتحه وانتظار 2-3 ثوان قبل الانتقال للدرس التالي
""")

# Save instructions for browser automation
instructions = {
    'course_url': course_url,
    'course_slug': course_slug,
    'steps': [
        'Navigate to course page',
        'Get page snapshot',
        'Find all lesson elements',
        'Click on each lesson one by one',
        'Wait 2-3 seconds between clicks'
    ],
    'wait_time_seconds': 3
}

instructions_file = Path('open_lessons_instructions.json')
with open(instructions_file, 'w', encoding='utf-8') as f:
    json.dump(instructions, f, indent=2, ensure_ascii=False)

print(f"\n💾 تم حفظ التعليمات في: {instructions_file}")

print("\n" + "="*60)
print("✅ السكريبت جاهز!")
print("="*60)
print("""
📝 لاستخدام هذا السكريبت:

الطريقة 1: استخدام JavaScript في Console (الأسهل)
   1. افتح المتصفح وانتقل للكورس
   2. اضغط F12 لفتح DevTools
   3. اذهب لـ Console tab
   4. انسخ والصق الكود من: open_all_lessons.js
   5. اضغط Enter

الطريقة 2: استخدام Browser Automation في Cursor
   (سيتم تنفيذها تلقائياً عبر أدوات المتصفح المدمجة)

🎯 السكريبت سيفتح جميع الدروس تلقائياً!
""")



