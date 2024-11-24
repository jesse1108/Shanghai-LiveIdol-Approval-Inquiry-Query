import requests
import csv
from bs4 import BeautifulSoup
import re
import time

def get_links_and_titles(page_url, retries=3):
    for _ in range(retries):
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links_and_titles = []

            for tr in soup.find_all('tr', align='left'):
                td = tr.find('td')
                link = td.find('a', target='blank')
                if link:
                    title = link.text.strip()
                    url = 'http://wsbs.wgj.sh.gov.cn' + link['href']
                    links_and_titles.append((url, title))

            return links_and_titles
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(5)
    return []

def check_address_and_date_in_page(url, addresses, year, retries=3):
    for _ in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.text

            found_address = None
            for address in addresses:
                if address in text:
                    found_address = address
                    break

            if not found_address:
                return None

            date_pattern = re.compile(r'演出日期：\s*(\d{4})')
            match = date_pattern.search(text)
            if match:
                date_year = int(match.group(1))
                if date_year >= year:
                    return found_address
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(5)
    return None

def main():
    base_url = 'http://wsbs.wgj.sh.gov.cn/shwgj_ywtb/core/web/welcome/index!toResultNotice.action?flag=1'
    addresses_to_check = [
        '宜昌路179号', '延安西路1735号', '凯旋路851号', '愚园路1398号', '愚园路1250号',
        '万航渡后路19号', '虹许路731号', '长宁路999号', '重庆南路308号'
    ]
    year_to_check = 2023
    output_file = 'output.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Address', 'Title', 'URL'])

        page_number = 1
        while True:
            print(f'Checking page {page_number}...')
            page_url = f'{base_url}&pageDoc.pageNo={page_number}'
            links_and_titles = get_links_and_titles(page_url)

            if not links_and_titles:
                break

            for url, title in links_and_titles:
                found_address = check_address_and_date_in_page(url, addresses_to_check, year_to_check)
                if found_address:
                    print(f'Found address {found_address} and date in: {title}\nURL: {url}\n')
                    csvwriter.writerow([found_address, title, url])

            page_number += 1

            if page_number % 11 == 0:
                print('Waiting for 30 seconds...')
                time.sleep(30)

if __name__ == '__main__':
    main()