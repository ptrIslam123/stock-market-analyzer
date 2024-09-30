import re
import time
import json

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup

DEEPSEEK_CONTEXT_PATH = "/home/islam/PycharmProjects/stock-market-analyzer/.local/deepseek_context"
DEEPSEEK_LOGIN_INFO_PATH = "/home/islam/PycharmProjects/stock-market-analyzer/.local/deepseek_login.json"

def run(playwright: Playwright) -> None:
    with open(DEEPSEEK_LOGIN_INFO_PATH, 'r', encoding='utf-8') as file:
        json_content = file.read()
        data = json.loads(json_content)
        login = data['user']['login']
        password = data['user']['password']

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://chat.deepseek.com/coder")
    page.goto("https://chat.deepseek.com/sign_in")
    page.get_by_placeholder("Phone number / email address").click()
    page.get_by_placeholder("Phone number / email address").fill(login)
    page.get_by_placeholder("Password").click()
    page.get_by_placeholder("Password").fill(password)
    page.locator(".ds-checkbox").click()
    page.get_by_role("button", name="Log in", exact=True).click()

    page.get_by_placeholder("Send a message").click()
    page.get_by_placeholder("Send a message").fill("What do you know about finance and assets?")
    page.get_by_role("button", name="Send").click()

    answer_block_element = None
    while True:
        try:
            soup = BeautifulSoup(page.content(), 'html.parser')
            answer_block_element = soup.find('div', class_='ds-markdown ds-markdown--block')
            time.sleep(2)
            if answer_block_element and answer_block_element.text == soup.find('div', class_='ds-markdown ds-markdown--block').text:
                break
        except:
            continue

    time.sleep(20)
    print(answer_block_element)

    page.get_by_text("Clear context").click()
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)