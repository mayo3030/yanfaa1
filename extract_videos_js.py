"""
Script to help extract video data from browser JavaScript console

Since the API only returns 1 video (promo), but the browser shows all 29 videos,
we need to extract the data from the browser's JavaScript memory/state.
"""

print("""
📋 Instructions to extract video data from browser:

1. Open Chrome/Firefox DevTools (F12)
2. Go to Console tab
3. Paste and run this JavaScript code:

```javascript
// Try to find Angular component or service with course data
let courseData = null;

// Method 1: Check window object
if (window.ng) {
    console.log('Angular found!');
    // Angular might store data in a service
}

// Method 2: Check localStorage/sessionStorage
console.log('localStorage:', Object.keys(localStorage));
console.log('sessionStorage:', Object.keys(sessionStorage));

// Method 3: Look for video/chapter data in DOM
let chapterElements = document.querySelectorAll('[class*="chapter"], [class*="lesson"], [class*="video"]');
console.log('Chapter/Lesson elements:', chapterElements.length);

// Method 4: Check for any data attributes
let dataElements = document.querySelectorAll('[data-video-id], [data-lesson-id], [data-chapter-id]');
console.log('Data elements:', dataElements.length);

// Method 5: Try to find Angular component instance (if Angular DevTools is installed)
// Or check for any global variables
console.log('Window properties:', Object.keys(window).filter(k => k.includes('course') || k.includes('video') || k.includes('lesson')));

// Method 6: Intercept network requests to see what data is loaded
// (Already done via browser network monitoring)

// Copy any relevant data and paste it here.
```

Alternatively, I can try to:
- Extract cookies from browser and use them with httpx
- Use browser automation to execute JavaScript and extract data
- Monitor network requests when clicking on lessons

Which approach would you prefer?
""")



