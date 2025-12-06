"""
استخراج جميع video IDs تلقائياً من صفحة الكورس وتحميلها
بدون الحاجة لفتح كل رابط يدوياً
"""
import json
import re
import time
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

print("="*60)
print("🚀 استخراج جميع video IDs تلقائياً من صفحة الكورس")
print("="*60)

# JavaScript code لاستخراج video IDs من الصفحة
extract_js = """
(async function() {
    const videoIds = [];
    const videoData = [];
    
    // الطريقة 1: اعتراض network requests للـ fetch
    const originalFetch = window.fetch;
    const interceptedIds = new Set();
    
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string') {
            // استخراج من Brightcove API URLs
            const brightcoveMatch = url.match(/brightcove\\.com.*\\/videos\\/(\\d+)/);
            if (brightcoveMatch) {
                interceptedIds.add(brightcoveMatch[1]);
            }
        }
        return originalFetch.apply(this, args);
    };
    
    // الطريقة 2: البحث في DOM عن عناصر الدروس
    const lessonElements = document.querySelectorAll('[data-video-id], [data-lesson-id], [class*="lesson"], [class*="chapter"], [class*="video-item"]');
    console.log('Found lesson elements:', lessonElements.length);
    
    // الطريقة 3: البحث عن جميع الأزرار/الروابط الخاصة بالدروس
    const lessonButtons = document.querySelectorAll('button[onclick*="lesson"], a[href*="lesson"], [class*="lesson-button"], [class*="chapter-item"]');
    console.log('Found lesson buttons/links:', lessonButtons.length);
    
    // الطريقة 4: البحث في Angular state أو React state
    let angularData = null;
    let reactData = null;
    
    // محاولة الوصول إلى Angular
    if (window.ng) {
        try {
            // محاولة الوصول إلى Angular component
            const app = document.querySelector('[ng-app], [ng-controller], [data-ng-app]');
            if (app) {
                angularData = app.getAttribute('ng-app') || app.getAttribute('ng-controller');
            }
        } catch(e) {}
    }
    
    // محاولة الوصول إلى React
    if (window.React || window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
        try {
            // البحث في React fiber
            const reactRoot = document.querySelector('#root, [data-reactroot]');
            if (reactRoot && reactRoot._reactInternalFiber) {
                reactData = 'React detected';
            }
        } catch(e) {}
    }
    
    // الطريقة 5: البحث في localStorage/sessionStorage
    const storageData = {
        localStorage: {},
        sessionStorage: {}
    };
    
    try {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.includes('course') || key.includes('lesson') || key.includes('video')) {
                storageData.localStorage[key] = localStorage.getItem(key);
            }
        }
    } catch(e) {}
    
    try {
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            if (key.includes('course') || key.includes('lesson') || key.includes('video')) {
                storageData.sessionStorage[key] = sessionStorage.getItem(key);
            }
        }
    } catch(e) {}
    
    // الطريقة 6: البحث في جميع scripts في الصفحة
    const scripts = document.querySelectorAll('script');
    let scriptData = [];
    
    scripts.forEach(script => {
        const content = script.textContent || script.innerText;
        // البحث عن Brightcove video IDs في scripts
        const matches = content.match(/videoId["']?\\s*[:=]\\s*["']?(\\d+)/gi);
        if (matches) {
            matches.forEach(match => {
                const idMatch = match.match(/(\\d+)/);
                if (idMatch) {
                    interceptedIds.add(idMatch[1]);
                }
            });
        }
        
        // البحث عن video IDs في JSON data
        const jsonMatches = content.match(/"brightcove_video_id"\\s*:\\s*"?(\\d+)"?/gi);
        if (jsonMatches) {
            jsonMatches.forEach(match => {
                const idMatch = match.match(/(\\d+)/);
                if (idMatch) {
                    interceptedIds.add(idMatch[1]);
                }
            });
        }
    });
    
    // الطريقة 7: النقر على جميع الدروس تلقائياً لجمع video IDs
    console.log('Starting automatic clicking on lessons...');
    
    const allLessonElements = Array.from(lessonButtons).length > 0 ? Array.from(lessonButtons) : Array.from(lessonElements);
    
    for (let i = 0; i < Math.min(allLessonElements.length, 30); i++) {
        try {
            const element = allLessonElements[i];
            const title = element.textContent?.trim() || element.getAttribute('title') || `Lesson ${i+1}`;
            
            // النقر على العنصر
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            await new Promise(resolve => setTimeout(resolve, 500));
            
            element.click();
            await new Promise(resolve => setTimeout(resolve, 2000)); // انتظار 2 ثانية
            
            console.log(`Clicked lesson ${i+1}: ${title}`);
        } catch(e) {
            console.error(`Error clicking lesson ${i+1}:`, e);
        }
    }
    
    // جمع جميع video IDs
    const allVideoIds = Array.from(interceptedIds);
    
    console.log('\\n=== Extraction Results ===');
    console.log('Video IDs found:', allVideoIds);
    console.log('Lesson elements:', lessonElements.length);
    console.log('Lesson buttons:', lessonButtons.length);
    console.log('Storage data:', Object.keys(storageData.localStorage).length + Object.keys(storageData.sessionStorage).length, 'items');
    
    return {
        videoIds: allVideoIds,
        lessonElements: lessonElements.length,
        lessonButtons: lessonButtons.length,
        storageData: storageData,
        angularData: angularData,
        reactData: reactData
    };
})();
"""

print(f"\n📋 الخطة:")
print(f"1. فتح صفحة الكورس: {course_url}")
print(f"2. تنفيذ JavaScript لاستخراج جميع video IDs")
print(f"3. النقر على جميع الدروس تلقائياً لجمع video IDs من network requests")
print(f"4. حفظ جميع video IDs في ملف JSON")
print(f"5. تحميل جميع الفيديوهات بشكل متوازي\n")

print("⏳ جاهز للبدء...")
print("💡 سيتم استخدام browser automation tools...\n")

# هذا الجزء سيتم تنفيذه باستخدام browser automation tools
# دعني أنشئ script منفصل يمكن تنفيذه في browser

# حفظ JavaScript code في ملف
js_file = output_dir / "extract_video_ids.js"
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(extract_js)

print(f"✅ تم حفظ JavaScript code في: {js_file}")
print("\n📝 التعليمات:")
print("1. افتح المتصفح واذهب إلى:", course_url)
print("2. افتح DevTools (F12) > Console")
print(f"3. انسخ محتوى الملف: {js_file}")
print("4. الصقه في Console واضغط Enter")
print("5. انتظر حتى ينتهي (سيستغرق بضع دقائق)")
print("6. انسخ النتيجة (JSON) والصقه في extract_results.json\n")

# إنشاء script لاستخدام browser automation مباشرة
print("\n🔧 أو يمكنني استخدام browser automation مباشرة...")
print("    (سأحتاج إلى أن تكون مسجل الدخول في المتصفح)\n")



