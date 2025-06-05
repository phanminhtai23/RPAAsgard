import re
import json
from datetime import datetime, timedelta

# 👉 Đọc file TypeScript với XPath selectors
INPUT_FILE = 'tests\output_xpath.spec.ts'  # <-- File có XPath selectors
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
        }

        time_offset += 1  # mỗi hành động cách nhau 3 giây

        # 👉 page.goto('url')
        if 'page.goto' in line:
            entry['action'] = 'navigate'
            match = re.search(r"goto\('([^']+)'", line)
            if match:
                entry['url'] = match.group(1)
                last_url = entry['url']

        # 👉 .fill(value) với XPath
        elif '.fill(' in line:
            entry['action'] = 'fill'
            # Extract XPath selector with xpath= prefix
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            value_match = re.search(r"fill\('([^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['value'] = value_match.group(1) if value_match else ''
            entry['url'] = last_url

        # 👉 .click() với XPath
        elif '.click' in line:
            entry['action'] = 'click'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['url'] = last_url

        # 👉 .press('key') với XPath
        elif '.press' in line:
            entry['action'] = 'press'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            key_match = re.search(r"press\('([^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['key'] = key_match.group(1) if key_match else ''
            entry['url'] = last_url

        # 👉 .check() với XPath
        elif '.check' in line:
            entry['action'] = 'check'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['url'] = last_url

        # 👉 .uncheck() với XPath
        elif '.uncheck' in line:
            entry['action'] = 'uncheck'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['url'] = last_url

        # 👉 .hover() với XPath
        elif '.hover' in line:
            entry['action'] = 'hover'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['url'] = last_url

        # 👉 .focus() với XPath
        elif '.focus' in line:
            entry['action'] = 'focus'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['url'] = last_url

        # 👉 .setInputFiles('filepath') với XPath
        elif '.setInputFiles' in line:
            entry['action'] = 'setInputFiles'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            file_match = re.search(r"setInputFiles\('([^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
            entry['file'] = file_match.group(1) if file_match else ''
            entry['url'] = last_url

        # 👉 .selectOption() với XPath
        elif '.selectOption' in line:
            entry['action'] = 'selectOption'
            xpath_match = re.search(r"locator\('(xpath=[^']+)'\)", line)
            option_match = re.search(r"selectOption\('([^']+)'\)", line)
            entry['selector'] = xpath_match.group(1) if xpath_match else ''
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

print(f"✅ Đã chuyển xong từ XPath TypeScript sang JSONL: {OUTPUT_FILE}")
