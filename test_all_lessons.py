import httpx
import json
from pathlib import Path

session_id = 'KbkcT1OsMgJt9x58hqwXDVKXAsz3DHPLMhF8AVLM'
course_slug = 'learning_english_level_one'
course_id = 69  # From previous API response

headers = {
    'Accept': 'application/json',
    'Origin': 'https://yanfaa.com',
    'Referer': f'https://yanfaa.com/us/single/{course_slug}'
}

# Try different endpoints
endpoints = [
    f'https://app.yanfaa.com/api/course/{course_slug}?session_id={session_id}',
    f'https://app.yanfaa.com/api/course/{course_slug}/lessons?session_id={session_id}',
    f'https://app.yanfaa.com/api/courses/{course_id}/lessons?session_id={session_id}',
    f'https://app.yanfaa.com/api/course/{course_id}/videos?session_id={session_id}',
    f'https://app.yanfaa.com/api/auth/courseProgress/{course_id}?session_id={session_id}',
]

print("🔍 Trying different endpoints to get all lessons...\n")

for url in endpoints:
    try:
        r = httpx.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ {url}")
            print(f"   Status: {r.status_code}")
            
            # Check for videos/lessons
            if isinstance(data, dict):
                if 'videos' in data:
                    print(f"   Videos: {len(data['videos'])}")
                if 'lessons' in data:
                    print(f"   Lessons: {len(data.get('lessons', []))}")
                if 'data' in data and isinstance(data['data'], list):
                    print(f"   Data items: {len(data['data'])}")
                    # Check first item
                    if data['data'] and isinstance(data['data'][0], dict):
                        print(f"   First item keys: {list(data['data'][0].keys())}")
            elif isinstance(data, list):
                print(f"   List items: {len(data)}")
            
            # Save if it looks promising
            if isinstance(data, dict) and ('videos' in data or 'lessons' in data):
                output_file = Path(f'output/lessons_api_{url.split("/")[-1].split("?")[0]}.json')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"   💾 Saved to {output_file}")
        else:
            print(f"❌ {url}")
            print(f"   Status: {r.status_code}")
    except Exception as e:
        print(f"❌ {url}")
        print(f"   Error: {str(e)[:100]}")
    print()



