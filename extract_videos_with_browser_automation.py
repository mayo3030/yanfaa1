"""
استخراج جميع video IDs باستخدام browser automation
يفتح الصفحة، ينقر على جميع الدروس، ويجمع video IDs من network requests
"""
import json
import re
import time
from pathlib import Path

course_slug = 'learning_english_level_one'
course_url = f'https://yanfaa.com/us/single/{course_slug}'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

print("="*60)
print("🤖 استخراج جميع video IDs باستخدام Browser Automation")
print("="*60)

print(f"\n📋 سأقوم بـ:")
print(f"1. فتح صفحة الكورس")
print(f"2. البحث عن قائمة الدروس")
print(f"3. النقر على كل درس تلقائياً")
print(f"4. جمع video IDs من network requests")
print(f"5. حفظ جميع video IDs\n")

print("⏳ جاهز للبدء...\n")

# قراءة الفيديوهات الموجودة
existing_videos_file = output_dir / "extracted_video_ids.json"
existing_videos = []
existing_brightcove_ids = set()

if existing_videos_file.exists():
    with open(existing_videos_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)
        existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}

print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")

# سيتم استدعاء browser automation tools هنا
# ولكن أولاً، دعني أنشئ helper function لاستخراج video IDs

def extract_video_ids_from_network(requests):
    """استخراج video IDs من network requests"""
    video_ids = []
    
    for req in requests:
        url = req.get('url', '') or req.get('request', {}).get('url', '')
        
        # البحث عن Brightcove video IDs
        brightcove_match = re.search(r'brightcove\.com.*?/videos/(\d+)', url)
        if brightcove_match:
            video_id = brightcove_match.group(1)
            if video_id not in existing_brightcove_ids:
                video_ids.append({
                    'brightcove_video_id': video_id,
                    'url': url
                })
    
    return video_ids

print("\n✅ Script جاهز!")
print("💡 سيتم استخدام browser automation tools لفتح الصفحة والنقر على الدروس\n")

# حفظ الإعدادات
config_file = output_dir / "extraction_config.json"
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump({
        'course_url': course_url,
        'course_slug': course_slug,
        'existing_videos_count': len(existing_videos),
        'target_total': 29
    }, f, indent=2, ensure_ascii=False)

print(f"💾 تم حفظ الإعدادات في: {config_file}\n")

# الآن سيتم استخدام browser tools
print("🚀 سأبدأ الآن باستخدام browser automation...")
print("📌 تأكد من أنك مسجل الدخول في المتصفح!\n")



