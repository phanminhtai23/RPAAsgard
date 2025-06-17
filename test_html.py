from multi_tool_agent.agent import get_html_content
from multi_tool_agent.agent import parse_ts_content

print(parse_ts_content("""

import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('https://voz.com/');
  await page.locator('section').filter({ hasText: 'Cloud Telecom Cloud Telecom' }).getByRole('link').nth(1).click();
  await page.locator('#price-card').getByRole('link', { name: 'Contratar' }).click();
  await page.getByText('Acepto la Política de Privacidad Enviar').click();
  await page.getByRole('textbox', { name: 'Nombre*' }).click();
  await page.getByRole('textbox', { name: 'Nombre*' }).fill('ahihi');
  await page.getByRole('textbox', { name: 'Nombre*' }).press('Tab');
  await page.getByRole('textbox', { name: 'Empresa (Opcional)' }).fill('ahihi');
});
"""))

# # Test get_html_content function
# result = get_html_content('https://youtube.com/', 'desktop')

# print("Status:", result['status'])
# print("Content length:", result.get('content_length', 0))

# if result['status'] == 'success':
#     html_content = result['html_content']
#     print("\n=== HTML PREVIEW (first 1000 chars) ===")
#     print(html_content[:1000])
    
#     # Look for navigation links
#     print("\n=== LOOKING FOR NAVIGATION LINKS ===")
#     if 'servicios' in html_content.lower():
#         print("✅ Found 'servicios' in HTML")
#     else:
#         print("❌ 'servicios' NOT found in HTML")
        
#     if 'distribuidor' in html_content.lower():
#         print("✅ Found 'distribuidor' in HTML")
#     else:
#         print("❌ 'distribuidor' NOT found in HTML")
        
#     # Look for title attributes
#     import re
#     title_matches = re.findall(r'title="([^"]*)"', html_content, re.IGNORECASE)
#     print(f"\n=== FOUND {len(title_matches)} TITLE ATTRIBUTES ===")
#     for i, title in enumerate(title_matches[:10]):  # Show first 10
#         print(f"{i+1}. title='{title}'")
        
#     # Look for href attributes with servicios/distribuidor
#     href_matches = re.findall(r'href="([^"]*(?:servicios|distribuidor)[^"]*)"', html_content, re.IGNORECASE)
#     print(f"\n=== FOUND {len(href_matches)} RELEVANT HREF ATTRIBUTES ===")
#     for i, href in enumerate(href_matches):
#         print(f"{i+1}. href='{href}'")
# else:
#     print("Error:", result.get('error_message', 'Unknown error')) 