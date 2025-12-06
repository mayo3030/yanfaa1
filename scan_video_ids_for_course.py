"""
Scan video IDs to find all 29 videos for learning_english_level_one course.
We know:
- Course ID: 69
- Video ID 1125 exists (promo) - Brightcove: 6253662723001
- Video ID 1136 exists (found in network) - Brightcove: 6247287755001
- Need to find the other 27 videos
"""
import httpx
import json
from pathlib import Path
import time

session_id = 'mNOaH74fU0c8w6cYFHGaA54wxqTq4fD5umworS16'
course_id = 69
course_slug = 'learning_english_level_one'

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"📚 Scanning video IDs for course {course_slug} (ID: {course_id})\n")
print(f"🔍 Known videos:")
print(f"   - Video ID 1125 (promo) - Brightcove: 6253662723001")
print(f"   - Video ID 1136 - Brightcove: 6247287755001\n")

output_dir = Path('output') / course_slug / 'videos'
output_dir.mkdir(parents=True, exist_ok=True)

all_videos = []
found_count = 0

# Strategy: Video IDs seem to be around 1100-1200 range
# Let's scan a wider range to find all 29 videos
print("🔍 Scanning video IDs...")
print("   (This may take a few minutes)\n")

# Try ranges around known video IDs
ranges_to_scan = [
    (1100, 1200),   # Around promo video (1125) and 1136
    (1000, 1100),   # Before promo
    (1200, 1300),   # After 1136
]

for start_id, end_id in ranges_to_scan:
    print(f"   Scanning IDs {start_id} to {end_id}...")
    for video_id in range(start_id, end_id):
        try:
            video_url = f'https://app.yanfaa.com/api/videos/{video_id}?session_id={session_id}'
            r = httpx.get(video_url, headers=headers, timeout=5)
            if r.status_code == 200:
                video_data = r.json()
                vid_course_id = video_data.get('course_id')
                
                # Check if this video belongs to our course (ID 69)
                if vid_course_id == course_id:
                    brightcove_id = video_data.get('brightcove_video_id')
                    title = video_data.get('title', f'Video {video_id}')
                    sort_order = video_data.get('sort', 0)
                    duration = video_data.get('duration', 0)
                    
                    video_info = {
                        'video_id': video_id,
                        'brightcove_video_id': brightcove_id,
                        'title': title,
                        'sort': sort_order,
                        'duration': duration,
                        'course_id': vid_course_id,
                    }
                    all_videos.append(video_info)
                    found_count += 1
                    print(f"   ✅ [{found_count}] ID {video_id}: {title[:50]} - Brightcove: {brightcove_id}")
                    
                    # If we found 29, we're done!
                    if found_count >= 29:
                        print(f"\n   🎉 Found all 29 videos!")
                        break
        except httpx.HTTPStatusError:
            pass  # Video doesn't exist or access denied
        except Exception as e:
            pass  # Other errors, continue
        
        # Small delay every 10 requests
        if video_id % 10 == 0:
            time.sleep(0.05)
    
    if found_count >= 29:
        break

# Sort by sort order
all_videos.sort(key=lambda x: x.get('sort', x.get('video_id', 0)))

# Save results
if all_videos:
    result = {
        'course_slug': course_slug,
        'course_id': course_id,
        'session_id': session_id,
        'total_found': len(all_videos),
        'expected_count': 29,
        'videos': all_videos
    }
    
    output_file = output_dir / 'all_videos_scanned.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(all_videos)} videos to {output_file}")
    print(f"\n📋 Summary:")
    print(f"   Expected: 29 videos")
    print(f"   Found: {len(all_videos)} videos")
    
    if len(all_videos) < 29:
        print(f"   ⚠️ Missing {29 - len(all_videos)} videos")
        print(f"   💡 Tip: May need to expand search range or check browser network requests")
    
    # Print all found videos
    print(f"\n📹 All found videos:")
    for i, v in enumerate(all_videos, 1):
        print(f"   {i:2d}. [{v['video_id']:4d}] {v['title'][:60]} - Brightcove: {v.get('brightcove_video_id', 'N/A')}")
    
    # Create download list
    download_list = []
    for v in all_videos:
        brightcove_id = v.get('brightcove_video_id')
        if brightcove_id:
            download_list.append({
                'video_id': v['video_id'],
                'title': v['title'],
                'brightcove_id': brightcove_id,
                'sort': v.get('sort', 0)
            })
    
    download_file = output_dir / 'download_list.json'
    with open(download_file, 'w', encoding='utf-8') as f:
        json.dump(download_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved download list ({len(download_list)} videos) to {download_file}")
else:
    print("\n⚠️ No videos found. May need to:")
    print("   1. Check if session_id is still valid")
    print("   2. Expand search range")
    print("   3. Check browser network requests when clicking lessons")

print("\n✅ Done!")



