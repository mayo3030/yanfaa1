"""
سكريبت بسيط لفتح/النقر على جميع الدروس تلقائياً
"""
import time
from pathlib import Path

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'

print("="*60)
print(f"🚀 فتح جميع الدروس تلقائياً")
print(f"📚 الكورس: {course_slug}")
print("="*60)

# Navigate to course page
print(f"\n🌐 الانتقال إلى: {course_url}")
print("   (سيتم فتح المتصفح تلقائياً)")

# Wait a bit for the page to load
print("\n⏳ انتظار تحميل الصفحة...")

print("\n" + "="*60)
print("📋 التعليمات:")
print("="*60)
print("""
1. تأكد من أنك قمت بتسجيل الدخول في المتصفح
2. افتح المتصفح في Cursor وانتقل إلى الكورس
3. سأقوم بالنقر على جميع الدروس تلقائياً

⚠️ ملاحظة: هذا السكريبت يستخدم أدوات المتصفح المدمجة في Cursor
   تحتاج إلى فتح المتصفح يدوياً أولاً، ثم سأنقر على الدروس

💡 بديل: يمكنك استخدام JavaScript Console في المتصفح:
""")

javascript_code = """
// النقر على جميع الدروس تلقائياً
(async function() {
    console.log('🚀 بدء النقر على جميع الدروس...');
    
    // البحث عن جميع عناصر الدروس
    const lessonSelectors = [
        '[role="listitem"]',  // List items (most common)
        '.lesson-item',
        '.chapter-item',
        'li[class*="lesson"]',
        'button[class*="lesson"]',
        'a[href*="lesson"]'
    ];
    
    let lessonElements = [];
    for (const selector of lessonSelectors) {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            lessonElements = Array.from(elements);
            console.log(`✅ تم العثور على ${elements.length} درس باستخدام: ${selector}`);
            break;
        }
    }
    
    // إذا لم نجد عناصر، نبحث في جميع العناصر القابلة للنقر
    if (lessonElements.length === 0) {
        const allClickable = document.querySelectorAll('li, button, a, [role="button"]');
        lessonElements = Array.from(allClickable).filter(el => {
            const text = el.textContent || el.innerText || '';
            return text.includes('Lesson') || text.includes('Le on') || 
                   text.includes('Introduction') || text.includes('برومو') ||
                   text.includes('intro') || text.includes('دروس');
        });
        console.log(`✅ تم العثور على ${lessonElements.length} درس محتمل`);
    }
    
    // تصفية العناصر الفريدة
    const uniqueLessons = [];
    const seenRefs = new Set();
    
    lessonElements.forEach((el, index) => {
        const text = (el.textContent || el.innerText || '').trim();
        const ref = el.getAttribute('data-ref') || el.id || `${el.tagName}-${index}`;
        
        if (text && text.length > 0 && !seenRefs.has(ref)) {
            seenRefs.add(ref);
            uniqueLessons.push({ element: el, text: text, ref: ref });
        }
    });
    
    console.log(`\\n📚 العدد الإجمالي للدروس: ${uniqueLessons.length}`);
    
    // النقر على كل درس
    for (let i = 0; i < uniqueLessons.length; i++) {
        const lesson = uniqueLessons[i];
        try {
            console.log(`\\n[${i+1}/${uniqueLessons.length}] 👆 النقر على: ${lesson.text.substring(0, 50)}`);
            
            // التمرير إلى العنصر
            lesson.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // النقر
            lesson.element.click();
            
            // انتظار تحميل الفيديو
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            console.log(`   ✅ تم النقر بنجاح`);
            
        } catch (error) {
            console.error(`   ❌ خطأ: ${error.message}`);
        }
    }
    
    console.log(`\\n✅ تم الانتهاء من النقر على ${uniqueLessons.length} درس!`);
})();
"""

# Save JavaScript code to file
js_file = Path('open_all_lessons.js')
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(javascript_code)

print(f"""
```javascript
{javascript_code}
```

📝 تم حفظ الكود في: {js_file}
💡 يمكنك نسخ الكود أعلاه ولصقه في Console في المتصفح (F12 > Console)

أو يمكنك استخدام أدوات المتصفح المدمجة في Cursor:
""")

print("\n" + "="*60)
print("✅ تم إنشاء السكريبت!")
print("="*60)
print(f"\n📁 الملفات:")
print(f"   - {js_file} - JavaScript code للاستخدام في Console")
print(f"\n💡 الطريقة الموصى بها:")
print("   1. افتح المتصفح في Cursor")
print("   2. انتقل إلى الكورس")
print("   3. افتح Console (F12)")
print("   4. انسخ والصق الكود من {js_file}")
print("   5. اضغط Enter")
print("\n🎯 سيتم النقر على جميع الدروس تلقائياً!")



