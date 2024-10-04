import argparse
import json
import re
from typing import Optional

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from global_configuration import *

def extract_title_and_url(news) -> Optional[tuple]:
    link = news.find('a')
    if link:
        url = link.get('href')
        title = link.text.strip()
        return title, url
    else:
        return None

def extract_post_date(news) -> Optional[str]:
    date = news.find('div', class_='news__date')
    if date:
        time_pattern = r'\b\d{2}:\d{2}\b'
        match = re.search(time_pattern, str(date.text))
        if match:
            return match.group(0)
    return None

def parse_info(page_content: str):
    data = list()
    soup = BeautifulSoup(page_content, 'html.parser')
    news_list = soup.find_all('div', class_='news__line')
    for news in news_list:
        post_date = extract_post_date(news)
        if post_date:
            title_and_url = extract_title_and_url(news)
            if title_and_url:
                title, url = title_and_url
                data.append({"post_date": post_date, "title": title, "url": url})

    return data

def run(playwright: Playwright, output_path: str) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(SMART_LAB_NEWS_URL)

    for _ in range(0, 30):
        try:
            page.get_by_text("Загрузить еще").click()
        except:
            break

    news_list = parse_info(page.content())
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(news_list, json_file, ensure_ascii=False, indent=4)

    # ---------------------
    context.close()
    browser.close()


def main():
    parser = argparse.ArgumentParser(description='Finam news publications analyzer')
    parser.add_argument('-f', '--outputfile', default='news_output.json',
                        help='Output file that will contains finam news publications analyzes')
    args = parser.parse_args()
    with sync_playwright() as playwright:
        run(playwright, args.outputfile)

if __name__ == "__main__":
    main()