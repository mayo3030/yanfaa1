import httpx
import json
from pathlib import Path
import subprocess
import sys

session_id = 'TzLot28kFSFgJuUbLVxzEnCw33TLZ7k9dTLvdMQt'

# Get course with all videos
url = f'https://app.yanfaa.com/api/course/Basics-of-photoshop?session_id={session_id}'
headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': 'https://yanfaa.com/us/single/Basics-of-photoshop'
}

r = httpx.get(url, headers=headers)
data = r.json()

print('=== Course Info ===')
print(f"Title: {data.get('title')}")
print(f"is_enrolled: {data.get('is_enrolled')}")

videos = data.get('videos', [])
print(f"Videos Count: {len(videos)}")

if not videos:
    print("\nNo videos found! The account may not be enrolled.")
    sys.exit(1)

print('\n=== All Videos ===')
for i, v in enumerate(videos):
    bc_id = v.get('brightcove_video_id', 'N/A')
    title = v.get('title', 'Unknown')
    print(f"{i+1}. {title[:50]} - Brightcove ID: {bc_id}")

# Save video info
output_dir = Path('output/Basics-of-photoshop/videos')
output_dir.mkdir(parents=True, exist_ok=True)

videos_info = []
for v in videos:
    videos_info.append({
        'id': v.get('id'),
        'title': v.get('title'),
        'brightcove_id': v.get('brightcove_video_id'),
        'duration': v.get('duration')
    })

with open(output_dir / 'all_videos_info.json', 'w', encoding='utf-8') as f:
    json.dump(videos_info, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved video info to {output_dir / 'all_videos_info.json'}")

# Try to download first video using ffmpeg if enrolled
if data.get('is_enrolled') and videos:
    print("\n🎬 Attempting to download first lesson...")
    first_video = videos[0]
    bc_id = first_video.get('brightcove_video_id')
    if bc_id:
        # Get HLS URL from Brightcove
        bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/6164421959001/videos/{bc_id}"
        bc_headers = {
            'Accept': 'application/json;pk=BCpkADawqM2QRYsRmY6RjR7_kxpL-RYC2FvGh4I5WRvwYiUHfYjjQNxNB6CpjKILFBLnHRW7hD8bMV7kDG4bTcSejh0LlIf1MCEHzV4NZ9_9L4xLp1FvU1sD0dxJaXnLLqxNHh5H'
        }
        try:
            bc_r = httpx.get(bc_url, headers=bc_headers)
            bc_data = bc_r.json()
            
            # Find HLS source
            sources = bc_data.get('sources', [])
            hls_url = None
            for src in sources:
                if 'application/x-mpegURL' in src.get('type', '') or '.m3u8' in src.get('src', ''):
                    hls_url = src.get('src')
                    break
            
            if hls_url:
                print(f"Found HLS URL for: {first_video.get('title')}")
                print(f"URL: {hls_url[:100]}...")
                
                # Download with ffmpeg
                safe_title = "".join(c for c in first_video.get('title', 'video')[:30] if c.isalnum() or c in ' -_')
                output_file = output_dir / f"01_{safe_title}.mp4"
                
                print(f"\n⬇️ Downloading to: {output_file}")
                result = subprocess.run([
                    'ffmpeg', '-i', hls_url, 
                    '-c', 'copy', 
                    '-y',
                    str(output_file)
                ], capture_output=True, text=True)
                
                if output_file.exists():
                    size_mb = output_file.stat().st_size / (1024 * 1024)
                    print(f"✅ Downloaded: {output_file.name} ({size_mb:.1f} MB)")
                else:
                    print(f"❌ Download failed")
                    print(result.stderr[-500:] if result.stderr else "No error output")
            else:
                print("No HLS URL found in video sources")
        except Exception as e:
            print(f"Error: {e}")
else:
    print("\n⚠️ Not enrolled or no videos - cannot download lessons")



