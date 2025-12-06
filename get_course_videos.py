import httpx
import json
from pathlib import Path

session_id = 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM'
course_slug = 'learning_english_level_one'

# Save session
session_file = Path('session.json')
session_file.write_text(json.dumps({'session_id': session_id}, indent=2))
print(f'Saved session_id to session.json')

# Get course data
url = f'https://app.yanfaa.com/api/course/{course_slug}?session_id={session_id}'
headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}'
}

r = httpx.get(url, headers=headers)
data = r.json()

print(f'Course: {data.get("title")}')
print(f'is_enrolled: {data.get("is_enrolled")}')
print(f'Videos count: {len(data.get("videos", []))}')

# Save course data
output_dir = Path('output') / course_slug
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / 'course_data.json').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Saved course data to {output_dir / "course_data.json"}')

# List videos
videos = data.get('videos', [])
print(f'\n=== Videos ({len(videos)}) ===')
for i, v in enumerate(videos):
    print(f'{i+1}. {v.get("title", "N/A")} - ID: {v.get("brightcove_video_id", "N/A")}')



