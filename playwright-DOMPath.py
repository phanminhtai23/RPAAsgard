from playwright.sync_api import sync_playwright
from playwright_dompath.dompath_sync import css_path, xpath_path

with sync_playwright() as p:
    url = "https://www.google.com/"
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    # Tìm ô tìm kiếm bằng role 'combobox' và name 'Tìm kiếm'
    searchBar_locator = page.get_by_role('combobox', name='Tìm kiếm')
    searchBar = searchBar_locator.element_handle()
    if searchBar is None:
        print("Không tìm thấy element!")
    else:
        # print("CSS Path:", css_path(searchBar))
        print("XPath:", xpath_path(searchBar))
    browser.close()