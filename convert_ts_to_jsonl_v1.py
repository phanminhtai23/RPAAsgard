import re
import json
from datetime import datetime, timedelta

# 👉 Đọc file TypeScript codegen đầu vào
INPUT_FILE = 'tests\output_xpath_full.spec.ts'  # <-- bạn có thể đổi tên file ở đây
OUTPUT_FILE = 'output3.jsonl'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

jsonl_lines = []
last_url = ''
start_time = datetime.utcnow()

time_offset = 0  # tính thời gian giả lập mỗi hành động

for line in lines:
    line = line.strip()

    if line.startswith('await page.'):
        entry = {
            'timestamp': (start_time + timedelta(seconds=time_offset)).isoformat(timespec='seconds') + 'Z',
            # 'generated_code': line
        }

        time_offset += 3  # mỗi hành động cách nhau 3 giây

        # 👉 page.goto('url')
        if 'page.goto' in line:
            entry['action'] = 'navigate'
            match = re.search(r"goto\('([^']+)'", line)
            if match:
                entry['url'] = match.group(1)
                last_url = entry['url']




        # 👉 .fill(selector, value)
        elif '.fill(' in line:
            entry['action'] = 'fill'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            value_match = re.search(r"fill\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['value'] = value_match.group(1) if value_match else ''
            entry['url'] = last_url

        # 👉 .click()
        elif '.click' in line:
            entry['action'] = 'click'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['url'] = last_url

        # 👉 .press('key')
        elif '.press' in line:
            entry['action'] = 'press'
            key_match = re.search(r"press\('([^']+)'\)", line)
            entry['key'] = key_match.group(1) if key_match else ''
            entry['url'] = last_url
        # 👉 .check()
        elif '.check' in line:
            entry['action'] = 'check'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['url'] = last_url

        # 👉 .uncheck()
        elif '.uncheck' in line:
            entry['action'] = 'uncheck'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['url'] = last_url

        # 👉 .hover()
        elif '.hover' in line:
            entry['action'] = 'hover'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['url'] = last_url

        # 👉 .focus()
        elif '.focus' in line:
            entry['action'] = 'focus'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['url'] = last_url

        # 👉 .setInputFiles('filepath')
        elif '.setInputFiles' in line:
            entry['action'] = 'setInputFiles'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            file_match = re.search(r"setInputFiles\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['file'] = file_match.group(1) if file_match else ''
            entry['url'] = last_url

        # 👉 .selectOption()
        elif '.selectOption' in line:
            entry['action'] = 'selectOption'
            selector_match = re.search(r"getBy[^.]+\(([^)]+)\)", line)
            option_match = re.search(r"selectOption\(([^)]+)\)", line)
            entry['selector'] = selector_match.group(1) if selector_match else ''
            entry['option'] = option_match.group(1) if option_match else ''
            entry['url'] = last_url
        # 👉 Các hành động khác
        else:
            entry['action'] = 'other'
            entry['url'] = last_url


        entry['generated_code'] = line
        jsonl_lines.append(json.dumps(entry, ensure_ascii=False))

# ✍️ Ghi ra file JSONL
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(jsonl_lines))

print(f"✅ Đã chuyển xong. File JSONL: {OUTPUT_FILE}")
