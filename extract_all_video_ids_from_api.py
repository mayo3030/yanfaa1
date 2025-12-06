"""
Extract all video IDs from Yanfaa API.
Since the user can access all lessons, we can use the API to get all video IDs.
"""
import httpx
import json
from pathlib import Path

# Session ID from login
session_id = 'mNOaH74fU0c8w6cYFHGaA54wxqTq4fD5umworS16'
course_slug = 'learning_english_level_one'

# Headers
headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Get course details first
print(f"📚 Fetching course details for: {course_slug}")
course_url = f'https://app.yanfaa.com/api/course/{course_slug}?session_id={session_id}'

try:
    r = httpx.get(course_url, headers=headers, timeout=30)
    r.raise_for_status()
    course_data = r.json()
    
    print(f"✅ Course: {course_data.get('title')}")
    print(f"📊 is_enrolled: {course_data.get('is_enrolled')}")
    
    # Try to find video IDs from different possible keys
    videos = []
    
    # Check different possible keys
    if 'videos' in course_data:
        videos = course_data['videos']
    elif 'lessons' in course_data:
        videos = course_data['lessons']
    elif 'course_lessons' in course_data:
        videos = course_data['course_lessons']
    
    print(f"📹 Found {len(videos)} videos/lessons in course data")
    
    # Try /api/courses/English/1 endpoint
    print("\n🔍 Trying /api/courses/English/1 endpoint...")
    try:
        courses_url = f'https://app.yanfaa.com/api/courses/English/1?session_id={session_id}'
        r = httpx.get(courses_url, headers=headers, timeout=30)
        if r.status_code == 200:
            courses_data = r.json()
            print(f"📊 Courses data keys: {list(courses_data.keys()) if isinstance(courses_data, dict) else 'List'}")
            
            # Check if it's a list or dict
            if isinstance(courses_data, list) and len(courses_data) > 0:
                # Find the course we want
                for course in courses_data:
                    if course.get('slug') == course_slug:
                        if 'videos' in course:
                            videos = course['videos']
                            print(f"✅ Found {len(videos)} videos from courses endpoint")
                            break
                        elif 'lessons' in course:
                            videos = course['lessons']
                            print(f"✅ Found {len(videos)} lessons from courses endpoint")
                            break
            elif isinstance(courses_data, dict):
                if 'videos' in courses_data:
                    videos = courses_data['videos']
                    print(f"✅ Found {len(videos)} videos from courses endpoint")
                elif 'lessons' in courses_data:
                    videos = courses_data['lessons']
                    print(f"✅ Found {len(videos)} lessons from courses endpoint")
    except Exception as e:
        print(f"⚠️ Error fetching courses: {e}")
    
    # If we still don't have videos, try fetching from /api/videos/{id} endpoints
    if not videos or len(videos) <= 1:
        print("\n🔍 Trying to fetch videos by ID from API...")
        print("   (This may take a while, scanning video IDs...)")
        video_ids_found = []
        
        # From network requests, we saw videos 1589, 1590, 1591 for level_two
        # For level_one, we need to try different ranges
        # Let's try multiple ranges
        ranges_to_try = [
            (1, 100),      # Low range
            (100, 500),    # Medium range
            (1000, 2000),  # Higher range (where we saw 1589-1591)
        ]
        
        for start_id, end_id in ranges_to_try:
            print(f"   Scanning IDs {start_id} to {end_id}...")
            for video_id in range(start_id, end_id):
                video_url = f'https://app.yanfaa.com/api/videos/{video_id}?session_id={session_id}'
                try:
                    r = httpx.get(video_url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        video_data = r.json()
                        brightcove_id = video_data.get('brightcove_video_id') or video_data.get('video_id')
                        title = video_data.get('title', f'Video {video_id}')
                        course_id = video_data.get('course_id') or video_data.get('course')
                        
                        # Check if this video belongs to our course
                        # We might need to filter by course_id or course_slug
                        if brightcove_id:
                            video_info = {
                                'lesson_id': video_id,
                                'title': title,
                                'brightcove_video_id': brightcove_id,
                                'course_id': course_id,
                                'api_url': video_url
                            }
                            video_ids_found.append(video_info)
                            print(f"   ✅ Found: {title} (ID: {video_id}) - Brightcove: {brightcove_id}")
                except Exception as e:
                    # Silently continue if video doesn't exist
                    pass
        
        if video_ids_found:
            videos = video_ids_found
            print(f"\n✅ Found {len(video_ids_found)} videos by scanning IDs")
    
    # Save results
    output_dir = Path('output') / course_slug / 'videos'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'all_video_ids.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'course_slug': course_slug,
            'session_id': session_id,
            'total_videos': len(videos),
            'videos': videos
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(videos)} video IDs to {output_file}")
    
    # Also save a simple list for downloading
    if videos:
        download_list = []
        for v in videos:
            brightcove_id = v.get('brightcove_video_id') or v.get('video_id')
            title = v.get('title', 'Unknown')
            if brightcove_id:
                download_list.append({
                    'title': title,
                    'brightcove_id': brightcove_id
                })
        
        download_file = output_dir / 'download_list.json'
        with open(download_file, 'w', encoding='utf-8') as f:
            json.dump(download_list, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved download list to {download_file}")
        print(f"\n📋 Video IDs found:")
        for i, v in enumerate(download_list, 1):
            print(f"  {i}. {v['title']} - {v['brightcove_id']}")

except httpx.HTTPStatusError as e:
    print(f"❌ HTTP Error: {e.response.status_code}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

