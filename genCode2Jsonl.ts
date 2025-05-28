import * as fs from 'fs';
import * as path from 'path';

// ✅ Đường dẫn tới file Playwright codegen
const inputFile = 'tests/test-2.spec.ts'; // thay bằng file thật nếu cần
const outputFile = 'output.jsonl';

const fileContent = fs.readFileSync(inputFile, 'utf-8');
const lines = fileContent.split('\n');

let jsonlOutput = '';
let lastUrl = '';
let timeOffset = 0;

function getTimestamp(offsetSeconds: number): string {
    const now = new Date(Date.now() + offsetSeconds * 1000);
    return now.toISOString();
}

for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.startsWith('await page.')) {
        const entry: any = {
            timestamp: getTimestamp(timeOffset),
            generated_code: trimmed,
        };

        timeOffset += 3; // Giả lập hành động mỗi 3 giây

        // 👉 page.goto()
        if (trimmed.includes('page.goto')) {
            entry.action = 'navigate';
            const urlMatch = trimmed.match(/'([^']+)'/);
            entry.url = urlMatch?.[1] || '';
            lastUrl = entry.url;
        }

        // 👉 page.fill()
        else if (trimmed.includes('.fill')) {
            entry.action = 'fill';
            const selectorMatch = trimmed.match(/getBy[^\.]+\(([^)]+)\)/);
            const valueMatch = trimmed.match(/fill\(([^)]+)\)/);
            entry.selector = selectorMatch?.[1] || '';
            entry.value = valueMatch?.[1] || '';
            entry.url = lastUrl;
        }

        // 👉 page.click()
        else if (trimmed.includes('.click')) {
            entry.action = 'click';
            const selectorMatch = trimmed.match(/getBy[^\.]+\(([^)]+)\)/);
            entry.selector = selectorMatch?.[1] || '';
            entry.url = lastUrl;
        }

        // 👉 page.press()
        else if (trimmed.includes('.press')) {
            entry.action = 'press';
            const keyMatch = trimmed.match(/press\('([^']+)'\)/);
            entry.key = keyMatch?.[1] || '';
            entry.url = lastUrl;
        }

        // 👉 Các hành động khác
        else {
            entry.action = 'other';
            entry.url = lastUrl;
        }

        jsonlOutput += JSON.stringify(entry) + '\n';
    }
}

// ✍️ Ghi file JSONL
fs.writeFileSync(outputFile, jsonlOutput, 'utf-8');
console.log(`✅ Đã ghi JSONL vào ${outputFile}`);
