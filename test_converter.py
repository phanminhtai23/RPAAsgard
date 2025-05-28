import unittest
from datetime import datetime
from convert_ts_to_jsonl import parse_line

class TestPlaywrightConverter(unittest.TestCase):

    def setUp(self):
        self.base_time = datetime(2025, 5, 28, 12, 0, 0)

    def test_goto(self):
        line = "await page.goto('https://example.com');"
        result, url = parse_line(line, '', self.base_time, 0)
        self.assertEqual(result['action'], 'navigate')
        self.assertEqual(result['url'], 'https://example.com')
        self.assertIn('goto', result['generated_code'])

    def test_fill(self):
        line = "await page.getByRole('textbox', { name: 'username' }).fill('testuser');"
        result, _ = parse_line(line, 'https://example.com', self.base_time, 3)
        self.assertEqual(result['action'], 'fill')
        self.assertIn("'testuser'", result['value'])
        self.assertEqual(result['url'], 'https://example.com')

    def test_click(self):
        line = "await page.getByRole('button', { name: 'Submit' }).click();"
        result, _ = parse_line(line, 'https://example.com', self.base_time, 6)
        self.assertEqual(result['action'], 'click')
        self.assertEqual(result['url'], 'https://example.com')

    def test_press(self):
        line = "await page.getByRole('textbox', { name: 'username' }).press('Enter');"
        result, _ = parse_line(line, 'https://example.com', self.base_time, 9)
        self.assertEqual(result['action'], 'press')
        self.assertEqual(result['key'], 'Enter')

    def test_unknown_action(self):
        line = "await expect(page).toHaveURL('https://example.com');"
        result, _ = parse_line(line, 'https://example.com', self.base_time, 12)
        self.assertEqual(result['action'], 'other')

if __name__ == '__main__':
    unittest.main()
