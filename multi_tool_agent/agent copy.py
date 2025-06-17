import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import logging
import sys
import re
import requests
from playwright.sync_api import sync_playwright
from google.adk.tools import LongRunningFunctionTool

# 🔧 Setup logging để debug
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 🌟 Biến toàn cục để cache HTML content theo URL và device type
HTML_CACHE = {}

def get_html_content_tool(url: str, device_type: str = "desktop") -> dict:
    """Uses Playwright to retrieve rendered HTML content (after JS execution), extracting <body> only."""

    print("🚀 FUNCTION CALLED: get_html_content", flush=True)
    print("📍 URL:", url, flush=True)
    print("📱 Device Type:", device_type, flush=True)
    logger.info(f"🚀 get_html_content called with URL: {url}, device_type: {device_type}")
    
    cache_key = f"{url}|{device_type.lower()}"
    if cache_key in HTML_CACHE:
        print("💾 USING CACHE for:", cache_key, flush=True)
        logger.info(f"💾 Using cache for: {cache_key}")
        cached_result = HTML_CACHE[cache_key].copy()
        cached_result["from_cache"] = True
        return cached_result

    try:
        with sync_playwright() as p:
            browser_type = p.webkit if device_type == "mobile" else p.chromium
            browser = browser_type.launch(headless=True)
            
            context = browser.new_context(
                **(browser.devices['iPhone 13'] if device_type == "mobile" else {})
            )
            page = context.new_page()
            page.goto(url, timeout=15000, wait_until='load')
            print("✅ Page loaded", flush=True)

            full_html = page.content()
            
            # Trích xuất body
            body_handle = page.query_selector('body')
            body_content = body_handle.inner_html() if body_handle else full_html
            body_wrapped = f"<body>{body_content}</body>" if body_handle else full_html
            
            print("✂️ Extracted rendered <body> content", flush=True)
            logger.info(f"✂️ Extracted rendered <body> content - Length: {len(body_wrapped)}")
            
            # 📦 Tạo result object
            result = {
                "status": "success",
                "html_content": body_wrapped,
                "status_code": 200,
                "content_length": len(body_wrapped),
                "original_length": len(full_html),
                "device_type": device_type,
                "from_cache": False,
                "rendered_with": "playwright"
            }
            
            HTML_CACHE[cache_key] = result.copy()
            return result
            
    except Exception as e:
        error_result = {
            "status": "error",
            "error_message": f"Playwright error for '{url}' with device '{device_type}': {str(e)}",
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

get_html_content = LongRunningFunctionTool(func=get_html_content_tool)

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
* Priority 2: Contextual Path with Ancestors (If No ID). If and only if the target element does not have a unique id, you MUST construct a contextual XPath. To do this, you must identify one or two of its direct, stable ancestors.
* You must then create a relative XPath that chains these elements together, starting from the ancestor(s) and moving to the target element.
* Use stable attributes (class, data-* attributes) or meaningful tag names (<nav>, <section>, <form>) to identify the ancestors.
* Note on Text Matching: When the condition for the target element relies on its text content (e.g., for a link or a button), you MUST use the normalize-space() function. This makes the locator robust against extra whitespace in the HTML.
* Correct: ...//button[normalize-space()='Log In']
* Incorrect: ...//button[text()='Log In']

  **CRITICAL**: The final XPath generated by either method **MUST** be unique and point to exactly one element. Do not add extra parents if an `id` is found.
c.  Replace the Line: Reconstruct the line using locator('xpath=YOUR_HYBRID_XPATH').

Final Output:

Return the complete, refactored script.
EXAMPLE (Updated with Hybrid Strategy and Normalize-Space Rule)

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
Check for ID: Assume the button does not have a unique ID.
Decision: Priority 1 fails. Apply Priority 2.
Find Ancestors: The button is inside a <form> with class js-login-form.
Construct Path: I will build the path from the form and identify the button by its text content, using normalize-space() as required.
Final XPath: //form[contains(@class, 'js-login-form')]//button[normalize-space()='Sign in']
Replace: await page.locator("xpath=//form[contains(@class, 'js-login-form')]//button[normalize-space()='Sign in']").click();
Final Output String:

TypeScript

import { test, expect } from '@playwright/test';

test('test', async (\{ page \}) => {
  await page.goto('https://github.com/login');
  await page.locator("xpath=//input[@id='login_field']").fill('testuser');
  await page.locator("xpath=//form[contains(@class, 'js-login-form')]//button[normalize-space()='Sign in']").click();
});
        """,
    tools=[get_html_content],
)

