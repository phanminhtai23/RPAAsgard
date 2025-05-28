import json
from datetime import datetime

input_file = './output_codegen.jsonl'
output_file = 'converted.jsonl'

converted_lines = []
current_url = ''  # Lưu URL hiện tại

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            timestamp = datetime.utcnow().isoformat(timespec='seconds') + "Z"
            action = data.get('name')
            entry = {
                "timestamp": timestamp,
                "action": action,
                "url": current_url,
            }

            if action == 'navigate':
                current_url = data['url']
                entry['url'] = current_url
                entry['generated_code'] = f"await page.goto('{current_url}');"

            elif action == 'click':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.click('{selector}');"

            elif action == 'fill':
                selector = data.get('selector', '')
                text = data.get('text', '')
                entry['selector'] = selector
                entry['value'] = text
                entry['generated_code'] = f"await page.fill('{selector}', '{text}');"

            elif action == 'press':
                selector = data.get('selector', '')
                key = data.get('key', '')
                entry['selector'] = selector
                entry['key'] = key
                entry['generated_code'] = f"await page.press('{selector}', '{key}');"

            elif action == 'openPage':
                continue  # bỏ qua openPage vì không cần xuất ra

            elif action == 'check':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.check('{selector}');"

            elif action == 'uncheck':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.uncheck('{selector}');"

            elif action == 'hover':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.hover('{selector}');"

            elif action == 'focus':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.focus('{selector}');"

            elif action == 'setInputFiles':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.setInputFiles('{selector}', 'file');"

            elif action == 'selectOption':
                selector = data.get('selector', '')
                entry['selector'] = selector
                entry['generated_code'] = f"await page.selectOption('{selector}', 'option');"

            else:
                continue  # bỏ qua các hành động không cần

            converted_lines.append(json.dumps(entry, ensure_ascii=False))
        except json.JSONDecodeError:
            continue

# Ghi ra file JSONL mới
with open(output_file, 'w', encoding='utf-8') as f:
    for line in converted_lines:
        f.write(line + '\n')

print(f"✅ Đã chuyển đổi xong! File output: {output_file}")
