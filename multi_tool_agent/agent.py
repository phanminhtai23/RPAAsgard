import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

import requests

def get_html_content(url: str, device_type: str = "desktop") -> dict:
    """Retrieves the HTML content from a specified URL with appropriate headers for device type.

    Args:
        url (str): The URL from which to retrieve the HTML content.
        device_type (str): Device type - "desktop" (default) or "mobile".

    Returns:
        dict: status and result or error msg containing the HTML content.
    """
    try:
        # Set headers based on device type
        if device_type.lower() == "mobile":
            # Mobile headers (iPhone user-agent)
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
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
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception cho HTTP error codes
        
        return {
            "status": "success",
            "html_content": response.text,
            "status_code": response.status_code,
            "content_length": len(response.text),
            "device_type": device_type,
            "user_agent": headers['User-Agent']
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve HTML content from '{url}' with device '{device_type}': {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "error_message": f"Unexpected error occurred while fetching '{url}' with device '{device_type}': {str(e)}"
        }



root_agent = Agent(
    name="root_agent",
    # model="gemini-2.5-flash-preview-05-20",
    model="gemini-2.0-flash",
    description=(
        "Agent converts test file playwright sang file that selects element by xpath"
    ),
    instruction="""
        You will receive the content of the .ts file which is the content of testing the website using playwright.

        FIRST, analyze the input file to detect if it uses mobile device configuration:
        - Look for "devices[" patterns (any mobile device like iPhone, iPad, Android, etc.)
        - Look for viewport settings with small width (< 600px) 
        - Look for test.use() with mobile device configurations

        DEVICE DETECTION RULES:
        - If input contains "devices[" → use get_html_content(url, "mobile")
        - If input has small viewport (width < 600px) → use get_html_content(url, "mobile")
        - If no mobile config detected → use get_html_content(url, "desktop") (default)

        Example input analysis:
        ```
        // Input has: devices['iPhone 13'] 
        // → Use: get_html_content(url, "mobile")

        // Input has: devices['iPad Pro']
        // → Use: get_html_content(url, "mobile") 

        // Input has: viewport: { width: 375, height: 667 }
        // → Use: get_html_content(url, "mobile")

        // Input has no devices[] or large viewport
        // → Use: get_html_content(url, "desktop")
        ```

        Example input with mobile device:
        ```
             import { test, expect, devices } from '@playwright/test';

             test.use({
             ...devices['iPhone 13'],
             colorScheme: 'dark',
             viewport: {
                 height: 600,
                 width: 800
             }
             });

            test('test', async (\{ page \}) => {
            await page.goto('https://github.com/microsoft/playwright');
            await page.getByRole('link', { name: 'Sign in' }).click();
            await page.getByRole('textbox', { name: 'Username or email address' }).click();
            await page.getByRole('textbox', { name: 'Username or email address' }).fill('phanminhtai23@gmai.com');
            await page.getByRole('textbox', { name: 'Username or email address' }).press('Tab');
            await page.getByRole('textbox', { name: 'Password' }).fill('Phanminhtai32');
            await page.getByRole('button', { name: 'Sign in' }).click();
            await page.goto('https://github.com/microsoft/playwright');
            });
        ```
        Your task is to convert the playwright element locator (page.getByRole(), page.getByText(), page.getByLabel(), page.getByPlaceholder(), page.getByAltText(), page.getByTitle(), page.getByTestId()) to element format using xpath.

        IMPORTANT RULES for XPath generation:
        1. ALWAYS create UNIQUE XPath selectors that target exactly ONE element
        2. Use multiple attributes to ensure uniqueness: @id, @class, @name, @placeholder, @aria-label, @data-testid, etc.
        3. Combine attributes when needed: //input[@placeholder="text" and @class="classname"]
        4. Use specific element tags instead of generic //* when possible
        5. Add position/index selectors like [1] or [last()] if multiple similar elements exist
        6. For mobile views, pay attention to mobile-specific classes and responsive design changes
        7. VERIFY uniqueness: After creating XPath, check in HTML that it matches only ONE element
        8. If XPath is too generic, add more attributes or use parent-child relationships
        9. Prioritize @id attribute if available as it's usually unique
        10. Use normalize-space() for exact text matching: //button[normalize-space()="Sign in"]

        MOBILE-SPECIFIC ANALYSIS:
        - Analyze HTML for each element in mobile mode
        - Use class or ID attributes to distinguish elements
        - Pay special attention to classes related to responsive display such as:
        + d-none, d-lg-inline-flex vs d-inline-flex
        + hidden-mobile, show-mobile, mobile-only
        + navbar-collapse, mobile-menu, desktop-nav
        - Mobile elements may have different classes than the desktop version of the same element
        - Check both mobile and desktop classes to create the correct XPath for each device type

        Example conversion:
        ```
             import { test, expect, devices } from '@playwright/test';

             test.use({
                 ...devices['iPhone 13'],
                 colorScheme: 'dark',
                 viewport: {
                     height: 600,
                     width: 800
                 }
             });

             test('test', async (\{ page \}) => {
                 await page.goto('https://github.com/microsoft/playwright');
                 // Mobile-specific XPath with multiple attributes
                 await page.locator('xpath=//a[normalize-space()="Sign in" and contains(@class, "HeaderMenu-link")]').click();
                 await page.locator('xpath=//input[@id="login_field" and @name="login"]').click();
                 await page.locator('xpath=//input[@id="login_field" and @name="login"]').fill('phanminhtai23@gmai.com');
                 await page.locator('xpath=//input[@id="login_field" and @name="login"]').press('Tab');
                 await page.locator('xpath=//input[@id="password" and @name="password"]').fill('Phanminhtai32');
                 await page.locator('xpath=//input[@name="commit" and @value="Sign in" and @type="submit"]').click();
                 await page.goto('https://github.com/microsoft/playwright');
             });
        ```

        Process:
        Step 1: Analyze input file to detect mobile device configuration
        Step 2: Use get_html_content(url, "mobile") if devices detected, otherwise get_html_content(url, "desktop")
        Step 3: Analyze the HTML structure to find exact elements with all attributes
        Step 4: Create UNIQUE XPath using multiple attributes that identify exactly ONE element
        Step 5: For each new URL, repeat steps 2-4 with same device type
        Step 6: Return complete .ts file with unique XPath selectors

        * CRITICAL: Each XPath MUST select exactly ONE element. If an XPath matches multiple elements, it MUST be made more specific by adding more attributes, using parent context, or adding position selectors. Use device-appropriate HTML (mobile vs desktop) for accurate selectors.

        """,
    tools=[get_html_content],
)