"""
استخراج جميع video IDs تلقائياً عبر النقر على جميع الدروس
"""
import json
import re
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# قائمة الدروس التي وجدتها من snapshot
lessons = [
    {"ref": "ref-gub22f8f04e", "name": "برومو - تعلم اللغة الإنجليزية ( المستوى الأول ) دقيقة"},
    {"ref": "ref-sna9d12rkko", "name": "Introduction دقيقتين"},
    {"ref": "ref-dcfamlgnr2", "name": "Le on 1 20 دقيقة"},
    {"ref": "ref-io7y7ulmb6", "name": "Le on 2 5 دقائق"},
    {"ref": "ref-7wgn6ll57c2", "name": "Le on 3 15 دقيقة"},
    {"ref": "ref-x25yrmwlvr", "name": "Le on 4 15 دقيقة"},
    {"ref": "ref-wa6w1tzp6r", "name": "Le on 5 12 دقيقة"},
    {"ref": "ref-qy6q36278z", "name": "Le on 6 9 دقائق"},
    {"ref": "ref-st0xkga6svs", "name": "Le on 7 9 دقائق"},
    {"ref": "ref-pt0bb8shj3o", "name": "Le on 8 11 دقيقة"},
    {"ref": "ref-izia3lgtv", "name": "Le on 9 13 دقيقة"},
    {"ref": "ref-9se2wk7rmh5", "name": "Le on 10 8 دقائق"},
    {"ref": "ref-nx2i9bvb57q", "name": "Le on 11 13 دقيقة"},
    {"ref": "ref-7bxpz44rlg9", "name": "Le on 12 14 دقيقة"},
    {"ref": "ref-8ck32a05n37", "name": "Le on 13 7 دقائق"},
    {"ref": "ref-j9ne1668v7", "name": "Le on 14 7 دقائق"},
    {"ref": "ref-hsw6dexysft", "name": "Le on 15 11 دقيقة"},
    {"ref": "ref-yk73ha7vbzd", "name": "Le on 16 12 دقيقة"},
    {"ref": "ref-itvevkqut6h", "name": "Le on 17 15 دقيقة"},
    {"ref": "ref-gmit2ya72ae", "name": "Le on 18 10 دقائق"},
    {"ref": "ref-6ha3rl2yzd5", "name": "Le on 19 10 دقائق"},
    {"ref": "ref-we6dkzmls1i", "name": "Le on 20 13 دقيقة"},
    {"ref": "ref-u15x6x2sfp8", "name": "Le on 21 8 دقائق"},
    {"ref": "ref-398n02clyv", "name": "Le on 22 10 دقائق"},
    {"ref": "ref-gr3f3pex3zg", "name": "Le on 23 9 دقائق"},
    {"ref": "ref-86ga2v53zed", "name": "Le on 24 10 دقائق"},
    {"ref": "ref-yzv2bhzc1gg", "name": "Le on 25 11 دقيقة"},
    {"ref": "ref-s6h0owplgyp", "name": "Le on 26 11 دقيقة"},
    {"ref": "ref-nl5f58jzenr", "name": "Le on 27 9 دقائق"},
    {"ref": "ref-mr871rwd93", "name": "Le on 28 9 دقائق"},
]

print(f"📚 وجدت {len(lessons)} درس")
print("🚀 سأبدأ بالنقر على كل درس وجمع video IDs من network requests...\n")

extracted_videos = []
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_brightcove_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)
        existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}

print(f"📊 الفيديوهات الموجودة: {len(existing_brightcove_ids)}")

# الآن سأستخدم browser automation للنقر على كل درس
# ولكن أولاً، دعني أنشئ script JavaScript لاستخراج video IDs مباشرة

javascript_extractor = """
// اعتراض جميع network requests
const videoIds = new Set();
const originalFetch = window.fetch;
const originalXHR = window.XMLHttpRequest.prototype.open;

// اعتراض Fetch
window.fetch = function(...args) {
    const url = args[0];
    if (typeof url === 'string' && url.includes('brightcove.com')) {
        const match = url.match(/\\/videos\\/(\\d+)/);
        if (match) {
            videoIds.add(match[1]);
            console.log('Found video ID:', match[1]);
        }
    }
    return originalFetch.apply(this, args);
};

// اعتراض XHR
window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    if (typeof url === 'string' && url.includes('brightcove.com')) {
        const match = url.match(/\\/videos\\/(\\d+)/);
        if (match) {
            videoIds.add(match[1]);
            console.log('Found video ID:', match[1]);
        }
    }
    return originalXHR.apply(this, [method, url, ...rest]);
};

// النقر على جميع الدروس
const lessonElements = document.querySelectorAll('[role="listitem"]');
console.log('Found lesson elements:', lessonElements.length);

for (let i = 0; i < lessonElements.length; i++) {
    const element = lessonElements[i];
    const text = element.textContent || element.innerText;
    if (text.includes('Lesson') || text.includes('Le on') || text.includes('Introduction') || text.includes('برومو')) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await new Promise(resolve => setTimeout(resolve, 500));
        element.click();
        await new Promise(resolve => setTimeout(resolve, 2000));
        console.log(`Clicked lesson ${i+1}: ${text}`);
    }
}

console.log('All video IDs:', Array.from(videoIds));
return Array.from(videoIds);
"""

# حفظ JavaScript code
js_file = output_dir / "extract_all_video_ids.js"
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(javascript_extractor)

print(f"\n✅ تم إنشاء JavaScript extractor في: {js_file}")
print("\n📋 الآن سأستخدم browser automation للنقر على جميع الدروس...\n")

# سأستخدم browser tools الآن للنقر على الدروس



