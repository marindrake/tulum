import json
from playwright.sync_api import sync_playwright

url = 'http://localhost:8000/'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')

    def read_menu():
        page.wait_for_selector('#menuColumns .menu-col ul li .item', timeout=10000)
        items = page.query_selector_all('#menuColumns .menu-col ul li .item')
        return [i.inner_text().strip() for i in items[:6]]

    # wait for translations to load
    try:
        page.wait_for_function('window.TRANSLATIONS !== null', timeout=5000)
    except Exception:
        pass

    result = {}
    result['initial_lang'] = page.evaluate('window.LANG || localStorage.getItem("tulum_lang") || null')
    result['before'] = read_menu()

    page.click('#langEN')
    page.wait_for_timeout(400)
    result['en'] = read_menu()

    page.click('#langFR')
    page.wait_for_timeout(400)
    result['fr'] = read_menu()

    page.click('#langES')
    page.wait_for_timeout(400)
    result['es'] = read_menu()

    print(json.dumps(result, ensure_ascii=False, indent=2))
    browser.close()
