"""
استخراج جميع video IDs تلقائياً من خلال النقر على جميع الدروس
"""
import json
import re
import time
from pathlib import Path

course_slug = 'learning_english_level_one'
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "extracted_video_ids.json"

# قراءة الفيديوهات الموجودة
existing_videos = []
if output_file.exists():
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_videos = json.load(f)

existing_brightcove_ids = {v['brightcove_video_id'] for v in existing_videos}
existing_yanfaa_ids = {v['yanfaa_video_id'] for v in existing_videos}

print("="*60)
print(f"🚀 استخراج جميع video IDs تلقائياً")
print(f"📚 الكورس: {course_slug}")
print(f"📊 الفيديوهات الموجودة: {len(existing_videos)}")
print(f"🎯 الهدف: 29 درس")
print("="*60)

# Navigate to course page
_browser_navigate(f"https://yanfaa.com/us/single/{course_slug}")
_browser_wait_for(3)

# Get page snapshot
snapshot = _browser_snapshot()

# Find all lesson elements
# Lessons are typically in list items with "Lesson" or "Le on" in the name
def find_lesson_elements(element, found=None):
    if found is None:
        found = []
    
    if element.get('role') == 'listitem':
        name = element.get('name', '')
        if any(keyword in name.lower() for keyword in ['lesson', 'le on', 'intro', 'promo', 'برومو']):
            found.append(element)
    
    for child in element.get('children', []):
        find_lesson_elements(child, found)
    
    return found

lesson_elements = find_lesson_elements(snapshot)

# Filter unique lessons by ref
unique_lessons = {}
for lesson in lesson_elements:
    ref = lesson.get('ref')
    name = lesson.get('name', 'Unknown')
    if ref and ref not in unique_lessons:
        unique_lessons[ref] = {'element': lesson, 'name': name}

lessons_to_process = list(unique_lessons.values())
print(f"\n✅ تم العثور على {len(lessons_to_process)} درس في الصفحة\n")

newly_found_videos = []

for i, lesson_info in enumerate(lessons_to_process):
    lesson_name = lesson_info['name']
    lesson_ref = lesson_info['element']['ref']
    
    print(f"[{i+1}/{len(lessons_to_process)}] 🖱️ النقر على: {lesson_name}")
    
    # Clear network requests before clicking
    _browser_network_requests(clear=True)
    
    # Click on lesson
    _browser_click(lesson_ref)
    _browser_wait_for(3)  # Wait for video to load
    
    # Get network requests
    requests = _browser_network_requests()
    
    brightcove_id = None
    yanfaa_video_id = None
    
    # Extract video IDs from network requests
    for req in requests:
        url = req.get('url', '')
        
        # Look for Brightcove playback API
        if "edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/" in url:
            match = re.search(r'/videos/(\d+)', url)
            if match:
                brightcove_id = match.group(1)
                print(f"   ✅ Brightcove ID: {brightcove_id}")
        
        # Look for Yanfaa API video endpoint
        if "app.yanfaa.com/api/videos/" in url and req.get('method') == 'GET':
            match = re.search(r'/api/videos/(\d+)', url)
            if match:
                yanfaa_video_id = int(match.group(1))
                print(f"   ✅ Yanfaa Video ID: {yanfaa_video_id}")
        
        # Also check promos endpoint
        if "app.yanfaa.com/api/promos/" in url and req.get('method') == 'GET':
            match = re.search(r'/api/promos/(\d+)', url)
            if match:
                yanfaa_video_id = int(match.group(1))
                print(f"   ✅ Yanfaa Promo ID: {yanfaa_video_id}")
    
    # Save if we found new video
    if brightcove_id and yanfaa_video_id:
        if brightcove_id not in existing_brightcove_ids and yanfaa_video_id not in existing_yanfaa_ids:
            newly_found_videos.append({
                "yanfaa_video_id": yanfaa_video_id,
                "brightcove_video_id": brightcove_id,
                "title": lesson_name
            })
            existing_brightcove_ids.add(brightcove_id)
            existing_yanfaa_ids.add(yanfaa_video_id)
            print(f"   ➕ فيديو جديد: {lesson_name}")
        else:
            print(f"   ℹ️ الفيديو موجود بالفعل: {lesson_name}")
    else:
        print(f"   ⚠️ لم يتم العثور على video IDs لـ: {lesson_name}")

# Merge with existing videos
all_videos_dict = {v['yanfaa_video_id']: v for v in existing_videos}
for new_video in newly_found_videos:
    all_videos_dict[new_video['yanfaa_video_id']] = new_video

# Convert to sorted list
all_videos_list = sorted(all_videos_dict.values(), key=lambda x: x['yanfaa_video_id'])

# Save results
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_videos_list, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print(f"📊 النتائج النهائية:")
print(f"✅ إجمالي الفيديوهات: {len(all_videos_list)}")
print(f"➕ فيديوهات جديدة: {len(newly_found_videos)}")
print(f"🎯 الهدف: 29 درس")
print("="*60)

if newly_found_videos:
    print("\n📋 الفيديوهات الجديدة:")
    for video in newly_found_videos:
        print(f"   - {video['title']} (ID: {video['yanfaa_video_id']}, Brightcove: {video['brightcove_video_id']})")

print("\n📋 جميع الفيديوهات:")
for i, video in enumerate(all_videos_list, 1):
    print(f"   {i:2d}. [{video['yanfaa_video_id']:4d}] {video['title']}")

print(f"\n💾 تم حفظ جميع video IDs في: {output_file}")

if len(all_videos_list) < 29:
    print(f"\n⚠️ لا تزال توجد {29 - len(all_videos_list)} فيديو مفقود")
else:
    print("\n✅ تم العثور على جميع الفيديوهات!")



