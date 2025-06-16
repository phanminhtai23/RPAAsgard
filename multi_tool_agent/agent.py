import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import logging
import sys

import requests

# 🔧 Setup logging để debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 🌟 Biến toàn cục để cache HTML content theo URL và device type
HTML_CACHE = {}

def get_html_content(url: str, device_type: str = "desktop") -> dict:
    """Retrieves the HTML content from a specified URL with appropriate headers for device type.
    Uses global cache to avoid re-fetching same URL+device_type combination.

    Args:
        url (str): The URL from which to retrieve the HTML content.
        device_type (str): Device type - "desktop" (default) or "mobile".

    Returns:
        dict: status and result or error msg containing the HTML content.
    """
    # 🔑 Tạo cache key dựa trên URL và device type
    
    print("🚀 FUNCTION CALLED: get_html_content", flush=True)
    print("📍 URL:", url, flush=True)
    print("📱 Device Type:", device_type, flush=True)
    logger.info(f"🚀 get_html_content called with URL: {url}, device_type: {device_type}")
    
    cache_key = f"{url}|{device_type.lower()}"
    
    # 🎯 Kiểm tra cache trước khi fetch
    if cache_key in HTML_CACHE:
        print("💾 USING CACHE for:", cache_key, flush=True)
        logger.info(f"💾 Using cache for: {cache_key}")
        cached_result = HTML_CACHE[cache_key].copy()
        cached_result["from_cache"] = True
        return cached_result
    
    print("🌐 FETCHING NEW DATA for:", cache_key, flush=True)
    logger.info(f"🌐 Fetching new data for: {cache_key}")
    
    try:
        # Set headers based on device type
        if device_type.lower() == "mobile":
            # Mobile headers (iPhone user-agent)
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Viewport-Width': '390'
            }
        else:
            # Desktop headers (default)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception cho HTTP error codes

        # ✨ Logic xử lý encoding chuẩn và an toàn nhất
        # 1. Lấy `response.content` để `requests` tự động giải nén (decompress).
        content_bytes = response.content
        
        # 2. Đoán encoding chính xác từ nội dung bytes đã giải nén.
        encoding_to_use = response.apparent_encoding or 'utf-8'
        
        print(f"✅ Using determined encoding: '{encoding_to_use}'", flush=True)
        logger.info(f"✅ Using determined encoding: '{encoding_to_use}'")
        
        # 3. Decode bytes thành string với encoding đã xác định.
        full_html = content_bytes.decode(encoding_to_use, errors='replace')
        
        # 🎯 Chỉ lấy phần body để tiết kiệm context window
        body_start = full_html.find('<body')
        body_end = full_html.find('</body>') + 7  # +7 để bao gồm </body>
        
        
        if body_start != -1 and body_end != -1:
            body_content = full_html[body_start:body_end]
            print("✂️ EXTRACTED BODY ONLY - Length:", len(body_content), flush=True)
            logger.info(f"✂️ Extracted body only - Length: {len(body_content)}")
        else:
            # Nếu không tìm thấy body tag, trả về toàn bộ
            body_content = full_html
            print("⚠️ NO BODY TAG FOUND - Using full HTML", flush=True)
            logger.warning("⚠️ No body tag found - Using full HTML")
        
        save_html_to_file(body_content, "html_content.html")

        # 📦 Tạo result object
        result = {
            "status": "success",
            "html_content": body_content,
            "status_code": response.status_code,
            "content_length": len(body_content),
            "original_length": len(full_html),
            "device_type": device_type,
            "user_agent": headers['User-Agent'],
            "from_cache": False
        }
        
        # 💾 Lưu vào cache cho lần sau
        HTML_CACHE[cache_key] = result.copy()
        
        print("📊 Body content length:", len(body_content), flush=True)
        print("📊 Original HTML length:", len(full_html), flush=True)
        print("📄 Body content preview:", body_content[:300], flush=True)
        return result
        
    except requests.exceptions.RequestException as e:
        error_result = {
            "status": "error",
            "error_message": f"Failed to retrieve HTML content from '{url}' with device '{device_type}': {str(e)}",
            "from_cache": False
        }
        return error_result
    except Exception as e:
        error_result = {
            "status": "error", 
            "error_message": f"Unexpected error occurred while fetching '{url}' with device '{device_type}': {str(e)}",
            "from_cache": False
        }
        return error_result

# 🧹 Hàm tiện ích để xóa cache khi cần
def clear_html_cache():
    """Clears the global HTML cache."""
    global HTML_CACHE
    HTML_CACHE.clear()

# 📊 Hàm tiện ích để xem thông tin cache
def get_cache_info():
    """Returns information about the current cache state."""
    return {
        "cache_size": len(HTML_CACHE),
        "cached_urls": list(HTML_CACHE.keys())
    }

def save_html_to_file(html_content: str, filename: str) -> dict:
    """Lưu nội dung HTML vào file.

    Args:
        html_content (str): Nội dung HTML cần lưu.
        filename (str): Tên file để lưu.

    Returns:
        dict: Kết quả trạng thái và thông báo.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return {
            "status": "success",
            "message": f"Đã lưu HTML vào file {filename} thành công!"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Lỗi khi lưu file: {str(e)}"
        }

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash-preview-05-20",
    # model="gemini-2.0-flash",
    description=(
        "Agent converts test file playwright sang file that selects element by xpath"
    ),
    instruction="""
You are an expert AI assistant specializing in refactoring Playwright test scripts. Your mission is to receive a string containing .ts test code and convert all Playwright locators (e.g., getByRole) into a unique, stable XPath locator based on a strict, prioritized strategy. You must not invent or assume any information not present in the provided code and the fetched HTML.

AVAILABLE TOOLS

You have access to the following function:

Python

def get_html_content(url: str, device_type: str = "desktop") -> dict:
 Retrieves the HTML content from a specified URL with appropriate headers for the device type.
 Uses a global cache to avoid re-fetching the same URL+device_type combination.

 Args:
  url (str): The URL from which to retrieve the HTML content.
  device_type (str): Device type - "desktop" (default) or "mobile".

 Returns:
  dict: A dictionary containing the status and result (the HTML content) or an error message.
 
STEP-BY-STEP INSTRUCTIONS

You MUST strictly follow these steps for every input script:

Global Analysis:

Read the entire input script.
Determine the device_type. If the script contains ...devices['...'], use device_type="mobile". Otherwise, use the default device_type="desktop".
Line-by-Line Processing:

Iterate through each line of the script.
Preserve any line that is not a Playwright action on an element (e.g., import, test.use, await page.goto(...)) exactly as it is.
Locator Conversion:

When you encounter a line with a non-XPath locator, perform the following sub-steps:
a.  Identify Current URL & Fetch HTML: Get the URL from the last page.goto() command and call get_html_content to fetch the page's HTML.
b.  Deduce Hybrid XPath: You MUST generate a unique XPath by following this strict, prioritized decision process:
* Priority 1: Direct ID Selection. First, inspect the target element itself within the fetched HTML. If the element has a unique id attribute, you MUST use this id to create the XPath. This is the most stable and preferred method. The process for this element stops here.
* Syntax: //TagName[@id='unique-id-value'] or simply //*[@id='unique-id-value']
* Priority 2: Contextual Path with Two Ancestors (If No ID). If and only if the target element does not have a unique id, you MUST construct a contextual XPath. To do this, you must identify two of its direct, stable ancestors (its parent and grandparent).
* You must then create a relative XPath that chains these three elements together, starting from the grandparent, moving to the parent, and finally to the target element.
* Use stable attributes (class, data-* attributes) or meaningful tag names (<nav>, <section>, <form>) to identify the ancestors.
* Syntax Example: //GrandparentTag[@class='...']//ParentTag[@class='...']//TargetTag[...conditions...]

  **CRITICAL**: The final XPath generated by either method **MUST** be unique and point to exactly one element. Do not add extra parents if an `id` is found.
c.  Replace the Line: Reconstruct the line using locator('xpath=YOUR_HYBRID_XPATH').

Final Output:

Return the complete, refactored script.
EXAMPLE (Updated with Hybrid Strategy)

Input String:

TypeScript

import { test, expect } from '@playwright/test';

test('test', async (\{ page \}) => {
  await page.goto('https://github.com/login');
  await page.getByLabel('Username or email address').fill('testuser');
  await page.getByRole('button', { name: 'Sign in' }).click();
});
Your (New) Thought Process:

Global Analysis & Setup: device_type is "desktop". URL is https://github.com/login. Call get_html_content.
Line 5: await page.getByLabel('Username or email address').fill('testuser');
Deduce XPath (Hybrid Process):
Check for ID: I inspect the input element in the HTML. I find it has id="login_field".
Decision: Priority 1 is met. I will use this ID.
Final XPath: //input[@id='login_field']
Replace: await page.locator("xpath=//input[@id='login_field']").fill('testuser');
Line 6: await page.getByRole('button', { name: 'Sign in' }).click();
Deduce XPath (Hybrid Process):
Check for ID: I inspect the 'Sign in' button. Let's assume for this example that it does not have a unique ID.
Decision: Priority 1 fails. I must now apply Priority 2: find two ancestors.
Find Ancestors: I look at the HTML. The button's direct parent is a div. That div's parent (the grandparent) is a <form> element which has a unique class js-login-form. These are my two stable ancestors.
Construct Path: I will build the path starting from the grandparent form.
Final XPath: //form[contains(@class, 'js-login-form')]/div/input[@type='submit']
Replace: await page.locator("xpath=//form[contains(@class, 'js-login-form')]/div/input[@type='submit']").click();
Final Output String:

TypeScript

import { test, expect } from '@playwright/test';

test('test', async (\{ page \}) => {
  await page.goto('https://github.com/login');
  await page.locator("xpath=//input[@id='login_field']").fill('testuser');
  await page.locator("xpath=//form[contains(@class, 'js-login-form')]/div/input[@type='submit']").click();
});
        """,
    tools=[get_html_content],
)