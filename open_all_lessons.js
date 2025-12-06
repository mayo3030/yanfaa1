
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
    
    console.log(`\n📚 العدد الإجمالي للدروس: ${uniqueLessons.length}`);
    
    // النقر على كل درس
    for (let i = 0; i < uniqueLessons.length; i++) {
        const lesson = uniqueLessons[i];
        try {
            console.log(`\n[${i+1}/${uniqueLessons.length}] 👆 النقر على: ${lesson.text.substring(0, 50)}`);
            
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
    
    console.log(`\n✅ تم الانتهاء من النقر على ${uniqueLessons.length} درس!`);
})();
