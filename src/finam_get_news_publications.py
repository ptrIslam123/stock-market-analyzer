import time
import json
import argparse

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from global_configuration import *

def parse_info(page_content: str):
    soup = BeautifulSoup(page_content, 'html.parser')

    data_publications_list = soup.find_all('div', class_='pt1x pb05x cl-grey')
    news_publications = dict()
    for data_publication in data_publications_list:
        title_element = data_publication.find('span', {'data-part': 'title'})
        if title_element:
            title = title_element.get_text(strip=True)
        else:
            title = str()

        link = data_publication.find('a')
        if link and link.get('href'):
            url = FINAM_URL + link.get('href')
        else:
            url = str()

        if len(title) > 0 and len(url) > 0:
            news_publications[title] = url

    return news_publications


def run(playwright: Playwright, output_path) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_URL)
    page.locator("#finfin-local-plugin-block-item-publication-list-infinity-item").get_by_text("Все", exact=True).click()

    for i in range(0, 15):
        try:
            page.get_by_role("button", name="Загрузить ещё").click()
            time.sleep(1)
        except Exception as e:
            print(str(e))
            break

    news_publications = parse_info(page.content())

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(news_publications, json_file, ensure_ascii=False, indent=4)
    # ---------------------
    context.close()
    browser.close()

def main(output_path: str):
    with sync_playwright() as playwright:
        run(playwright, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finam news publications analyzer')
    parser.add_argument('-f', '--outputfile', default='news_output.json', help='Output file that will contains finam news publications analyzes')
    args = parser.parse_args()
    main(args.outputfile)