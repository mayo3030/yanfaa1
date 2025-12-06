"""
Extract all lesson video IDs for learning_english_level_one course.
Since video_count is 29 but API only returns 1, we need to find the video IDs.
"""
import httpx
import json
from pathlib import Path
import time
from proxy_helper import get_httpx_client

session_id = 'mNOaH74fU0c8w6cYFHGaA54wxqTq4fD5umworS16'
course_id = 69  # From the API response
course_slug = 'learning_english_level_one'

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"📚 Course: {course_slug} (ID: {course_id})")
print(f"🎯 Looking for 29 videos...\n")

all_videos = []
found_count = 0

# Strategy: Try different endpoints and video ID ranges
# From network requests, we know video IDs exist for courses
# Let's try a smart approach - start from a reasonable range

# Method 1: Try /api/courses/{course_id}/lessons or similar
endpoints_to_try = [
    f'https://app.yanfaa.com/api/courses/{course_id}/lessons?session_id={session_id}',
    f'https://app.yanfaa.com/api/course/{course_slug}/lessons?session_id={session_id}',
    f'https://app.yanfaa.com/api/videos?course_id={course_id}&session_id={session_id}',
    f'https://app.yanfaa.com/api/courses/{course_id}/videos?session_id={session_id}',
]

print("🔍 Trying alternative API endpoints...")
for endpoint in endpoints_to_try:
    try:
        print(f"   Testing: {endpoint}")
        with get_httpx_client(headers=headers, timeout=10) as client:
            r = client.get(endpoint)
            if r.status_code == 200:
                data = r.json()
                print(f"   ✅ Status 200! Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                
                # Check if we got videos
                if isinstance(data, dict):
                    if 'data' in data and isinstance(data['data'], list):
                        videos = data['data']
                        if videos and len(videos) > 1:
                            all_videos = videos
                            print(f"   ✅ Found {len(videos)} videos!")
                            break
                    elif 'videos' in data:
                        videos = data['videos']
                        if videos and len(videos) > 1:
                            all_videos = videos
                            print(f"   ✅ Found {len(videos)} videos!")
                            break
                    elif 'lessons' in data:
                        videos = data['lessons']
                        if videos and len(videos) > 1:
                            all_videos = videos
                            print(f"   ✅ Found {len(videos)} videos!")
                            break
                elif isinstance(data, list) and len(data) > 1:
                    all_videos = data
                    print(f"   ✅ Found {len(data)} videos!")
                    break
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

# Method 2: If no luck, scan video IDs
# From the promo video, we know video ID 1125 exists
# Let's try ranges around this and other patterns
if not all_videos or len(all_videos) <= 1:
    print("\n🔍 Scanning video IDs...")
    print("   (This may take a few minutes)")
    
    # Try ranges: video IDs might be sequential or in a pattern
    ranges_to_try = [
        (1100, 1200),   # Around promo video (1125)
        (1500, 1650),   # Where we saw videos for level_two
        (100, 300),     # Lower range
    ]
    
    video_ids_found = []
    
    for start_id, end_id in ranges_to_try:
        print(f"   Scanning IDs {start_id} to {end_id}...")
        for video_id in range(start_id, end_id):
            try:
                video_url = f'https://app.yanfaa.com/api/videos/{video_id}?session_id={session_id}'
                with get_httpx_client(headers=headers, timeout=5) as client:
                    r = client.get(video_url)
                    if r.status_code == 200:
                        video_data = r.json()
                        brightcove_id = video_data.get('brightcove_video_id') or video_data.get('video_id')
                        title = video_data.get('title', f'Video {video_id}')
                        vid_course_id = video_data.get('course_id') or video_data.get('course')
                        
                        # Check if this video belongs to our course (ID 69)
                        if brightcove_id and (vid_course_id == course_id or vid_course_id == course_slug):
                            video_info = {
                                'id': video_id,
                                'lesson_id': video_id,
                                'title': title,
                                'brightcove_video_id': brightcove_id,
                                'course_id': vid_course_id,
                                'duration': video_data.get('duration'),
                                'sort': video_data.get('sort'),
                            }
                            video_ids_found.append(video_info)
                            found_count += 1
                            print(f"   ✅ [{found_count}] {title} (ID: {video_id}) - Brightcove: {brightcove_id}")
                            
                            # If we found 29, we're done!
                            if found_count >= 29:
                                print(f"\n   ✅ Found all 29 videos!")
                                break
            except Exception as e:
                pass
            
            # Small delay to avoid rate limiting
            if video_id % 10 == 0:
                time.sleep(0.1)
        
        if found_count >= 29:
            break
    
    if video_ids_found:
        # Sort by sort order or ID
        video_ids_found.sort(key=lambda x: x.get('sort', x.get('id', 0)))
        all_videos = video_ids_found

# Save results
output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

if all_videos:
    output_file = output_dir / 'all_lessons_found.json'
    
    result = {
        'course_slug': course_slug,
        'course_id': course_id,
        'session_id': session_id,
        'total_found': len(all_videos),
        'expected_count': 29,
        'videos': all_videos
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(all_videos)} videos to {output_file}")
    print(f"\n📋 Summary:")
    print(f"   Expected: 29 videos")
    print(f"   Found: {len(all_videos)} videos")
    
    if len(all_videos) < 29:
        print(f"   ⚠️ Missing {29 - len(all_videos)} videos - may need to check other ID ranges")
    
    # Create download list
    download_list = []
    for v in all_videos:
        brightcove_id = v.get('brightcove_video_id') or v.get('video_id')
        title = v.get('title', 'Unknown')
        if brightcove_id:
            download_list.append({
                'title': title,
                'brightcove_id': brightcove_id,
                'lesson_id': v.get('id') or v.get('lesson_id')
            })
    
    download_file = output_dir / 'download_list.json'
    with open(download_file, 'w', encoding='utf-8') as f:
        json.dump(download_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved download list to {download_file}")
    
    # Print first few for verification
    print(f"\n📹 Sample videos found:")
    for i, v in enumerate(download_list[:5], 1):
        print(f"   {i}. {v['title']} - {v['brightcove_id']}")
    if len(download_list) > 5:
        print(f"   ... and {len(download_list) - 5} more")
else:
    print("\n⚠️ Could not find video IDs. May need to check network requests manually.")

