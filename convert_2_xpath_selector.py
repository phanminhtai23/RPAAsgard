from pathlib import Path
import json
import re

# Đọc dữ liệu từ file jsonl giả định (dùng sample content vì không có file thật)
input_path = Path("output_codegen.jsonl")
output_path = Path("output_xpath.jsonl")

# Hàm chuyển selector sang dạng XPath cơ bản (chỉ demo một số kiểu phổ biến)
def convert_selector_to_xpath(selector: str) -> str:
    # Loại bỏ prefix nội bộ của Playwright nếu có
    if selector.startswith("internal:role="):
        match = re.search(r'name="([^"]+)"', selector)
        role = re.search(r'role=([^[]+)', selector)
        if role and match:
            return f'//{role.group(1)}[contains(text(), "{match.group(1)}")]'

    if selector.startswith("internal:attr="):
        match = re.search(r'\[title="([^"]+)"', selector)
        if match:
            return f'//*[@title="{match.group(1)}"]'

    if selector.startswith("internal:role=combobox"):
        match = re.search(r'name="([^"]+)"', selector)
        if match:
            return f'//input[@role="combobox" and contains(@aria-label, "{match.group(1)}")]'

    if selector.startswith("internal:role=link"):
        match = re.search(r'name="([^"]+)"', selector)
        if match:
            return f'//a[contains(text(), "{match.group(1)}")]'

    if selector.startswith("internal:role=button"):
        match = re.search(r'name="([^"]+)"', selector)
        if match:
            return f'//button[contains(text(), "{match.group(1)}")]'

    if selector.startswith("internal:has-text="):
        match = re.search(r'/\^?(.+?)\$?/', selector)
        if match:
            return f'//*[contains(text(), "{match.group(1)}")]'

    if selector.startswith("#"):
        return f'//*[@id="{selector[1:]}"]'

    if selector.startswith("."):
        return f'//*[contains(@class, "{selector[1:]}")]'

    if selector.startswith("xpath="):
        return selector[6:]

    return f'//{selector}'  # fallback

# Đọc và xử lý file
output_lines = []
with input_path.open("r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if "selector" in obj:
            original = obj["selector"]
            xpath = convert_selector_to_xpath(original)
            obj["selector_xpath"] = xpath  # Lưu XPath mới vào field mới
        output_lines.append(obj)

# Ghi ra file mới
with output_path.open("w", encoding="utf-8") as f:
    for obj in output_lines:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

output_path
