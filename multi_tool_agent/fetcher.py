import sys
from playwright.sync_api import sync_playwright
import os

def fetch_html(url: str, device_type: str = "desktop"):
    """
    Launches Playwright to fetch HTML and saves it to a temporary file
    to avoid Unicode issues with stdout on Windows.
    """
    output_file = "temp_html_output.html"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                if device_type.lower() == 'desktop'
                else 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                viewport={'width': 1280, 'height': 720} if device_type.lower() == 'desktop' else {'width': 390, 'height': 844},
            )
            page = context.new_page()
            page.goto(url, timeout=60000, wait_until='domcontentloaded')

            # Attempt to dismiss cookie consent pop-ups
            consent_selectors = [
                'button:has-text("Accept all")', 'button:has-text("I agree")',
                'button:has-text("Agree")', 'button:has-text("Accept")',
                '[aria-label="Accept all"]', '[aria-label="Agree to all"]'
            ]
            for selector in consent_selectors:
                try:
                    page.locator(selector).click(timeout=1500)
                    page.wait_for_timeout(2000)
                    break
                except Exception:
                    pass
            
            page.wait_for_timeout(3000)
            html_content = page.content()
            browser.close()

            # Ghi nội dung vào file tạm với encoding UTF-8
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

    except Exception as e:
        # Print any errors to standard error
        print(f"Fetcher Error: {type(e).__name__} - {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetcher.py <URL> [device_type]", file=sys.stderr)
        sys.exit(1)
    
    url_arg = sys.argv[1]
    device_type_arg = sys.argv[2] if len(sys.argv) > 2 else "desktop"
    
    fetch_html(url_arg, device_type_arg) 