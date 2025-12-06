"""
Extract all video IDs from /api/courses/English/1 endpoint
This seems to return all lessons for the English course.
"""
import httpx
import json
from pathlib import Path

session_id = 'mNOaH74fU0c8w6cYFHGaA54wxqTq4fD5umworS16'
course_slug = 'learning_english_level_one'
course_id = 69

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"📚 Extracting all videos for: {course_slug}\n")

output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

# Method 1: Try /api/courses/English/1
print("🔍 Method 1: Trying /api/courses/English/1...")
try:
    url = f'https://app.yanfaa.com/api/courses/English/1?session_id={session_id}'
    r = httpx.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    print(f"   ✅ Status: {r.status_code}")
    print(f"   📊 Response keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
    
    # Check if we got lessons/videos
    if isinstance(data, dict):
        # Try different possible keys
        lessons = data.get('lessons') or data.get('videos') or data.get('data', [])
        if isinstance(lessons, list) and len(lessons) > 0:
            print(f"   ✅ Found {len(lessons)} lessons/videos!")
            
            all_videos = []
            for lesson in lessons:
                video_id = lesson.get('id') or lesson.get('video_id')
                brightcove_id = lesson.get('brightcove_video_id') or lesson.get('brightcove_id')
                title = lesson.get('title', 'Unknown')
                
                if video_id:
                    all_videos.append({
                        'video_id': video_id,
                        'brightcove_video_id': brightcove_id,
                        'title': title,
                        'sort': lesson.get('sort', 0),
                        'duration': lesson.get('duration'),
                        'course_id': lesson.get('course_id', course_id),
                    })
            
            # Sort by sort order
            all_videos.sort(key=lambda x: x.get('sort', x.get('video_id', 0)))
            
            print(f"\n📹 Found {len(all_videos)} videos:")
            for i, v in enumerate(all_videos[:10], 1):
                print(f"   {i}. [{v['video_id']}] {v['title']} - Brightcove: {v.get('brightcove_video_id', 'N/A')}")
            if len(all_videos) > 10:
                print(f"   ... and {len(all_videos) - 10} more")
            
            # Save results
            result = {
                'course_slug': course_slug,
                'course_id': course_id,
                'session_id': session_id,
                'total_found': len(all_videos),
                'source': '/api/courses/English/1',
                'videos': all_videos
            }
            
            output_file = output_dir / 'all_lessons_from_courses_endpoint.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Saved to {output_file}")
            
            # If we got all videos, we're done!
            if len(all_videos) >= 29:
                print(f"\n🎉 Successfully found all {len(all_videos)} videos!")
            else:
                print(f"\n⚠️ Found {len(all_videos)} videos, expected 29. May need to check other methods.")
        else:
            print(f"   ⚠️ No lessons/videos found in response")
            print(f"   📄 Full response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
    else:
        print(f"   ⚠️ Unexpected response format: {type(data)}")
        if isinstance(data, list):
            print(f"   📊 List length: {len(data)}")
            if len(data) > 0:
                print(f"   📄 First item: {json.dumps(data[0], indent=2, ensure_ascii=False)[:300]}...")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Method 2: Try to fetch video 1136 that we saw in network requests
print(f"\n🔍 Method 2: Fetching video 1136 (found in network requests)...")
try:
    url = f'https://app.yanfaa.com/api/videos/1136?session_id={session_id}'
    r = httpx.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        video_data = r.json()
        print(f"   ✅ Video 1136: {video_data.get('title')} - Brightcove: {video_data.get('brightcove_video_id')}")
        print(f"   📊 Course ID: {video_data.get('course_id')}")
        
        # If it belongs to course 69, we can scan nearby IDs
        vid_course_id = video_data.get('course_id')
        if vid_course_id == course_id:
            print(f"   ✅ This video belongs to our course!")
            print(f"   🔍 We can scan video IDs around 1136...")
except Exception as e:
    print(f"   ⚠️ Could not fetch video 1136: {e}")

print("\n✅ Done!")



