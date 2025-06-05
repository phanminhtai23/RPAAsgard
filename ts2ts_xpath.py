import re

# Tên file input/output
input_file = 'tests\\output_xpath_full.spec.ts'
output_file = 'tests\\output_xpath.spec.ts'

# Hàm chuyển các hàm Playwright thành dạng XPath
def convert_to_xpath_selector(line: str) -> str:
    # getByTestId('royal-email') => xpath=//*[@data-testid="royal-email"]
    line = re.sub(
        r'getByTestId\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//*[@data-testid=\"\1\"]")',
        line
    )

    # getByRole('button', { name: 'Submit' }) => //*[(role logic) and normalize-space(text())="Submit"]
    def role_repl(match):
        role = match.group(1)
        props = match.group(2)
        name_match = re.search(r'name\s*:\s*[\'"]([^\'"]+)[\'"]', props)
        level_match = re.search(r'level\s*:\s*(\d+)', props)
        xpath = f'//{role}'
        if role == 'heading' and level_match:
            xpath = f'//h{level_match.group(1)}'
        if name_match:
            # Sửa chỗ này để dùng dấu nháy đơn trong XPath
            xpath += f'[contains(normalize-space(.), \\\"{name_match.group(1)}\\\")]'
        return f'locator("xpath={xpath}")'

    line = re.sub(
        r'getByRole\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*\{([^}]+)\}\)',
        role_repl,
        line
    )

    # getByText('Some Text') => xpath=//*[contains(text(),"Some Text")]
    line = re.sub(
        r'getByText\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//*[contains(text(),\"\1\")]")',
        line
    )

    # getByText('Exact Match', { exact: true }) => xpath=//*[text()="Exact Match"]
    line = re.sub(
        r'getByText\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*\{\s*exact\s*:\s*true\s*\}\)',
        r'locator("xpath=//*[text()=\"\1\"]")',
        line
    )
    
    # getByLabel('Label Text') => //*[@aria-label="Label Text"] or using label
    line = re.sub(
        r'getByLabel\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//label[contains(normalize-space(.),\"\1\")]/following::input[1]")',
        line
    )

    # getByPlaceholder('Search...') => //*[@placeholder="Search..."]
    line = re.sub(
        r'getByPlaceholder\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//*[@placeholder=\"\1\"]")',
        line
    )

    # getByAltText('Alt Text') => //img[@alt="Alt Text"]
    line = re.sub(
        r'getByAltText\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//img[@alt=\"\1\"]")',
        line
    )

    # getByTitle('Tooltip') => //*[@title="Tooltip"]
    line = re.sub(
        r'getByTitle\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        r'locator("xpath=//*[@title=\"\1\"]")',
        line
    )

    return line

# Đọc file, chuyển đổi, và ghi ra file mới
with open(input_file, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

with open(output_file, 'w', encoding='utf-8') as outfile:
    for line in lines:
        converted_line = convert_to_xpath_selector(line)
        outfile.write(converted_line)

print(f"Đã chuyển đổi thành công từ {input_file} sang {output_file}")