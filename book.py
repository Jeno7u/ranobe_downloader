import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
import os


headers = {
    'user-agent': UserAgent().random
}

def get_url():
    print('[+]Пример: https://ranobelib.me/sss-class-suicide-hunter')
    return input('[+]Введите ссылку: ')


def get_chapters_tags(url):
    driver = webdriver.Chrome()
    driver.get(url+'/v1/c1')
    driver.find_elements(By.CLASS_NAME, 'reader-header-action__text')[1].click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    return soup.find_all('a', class_='menu__item')


def get_soup(url):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            break
        print('[+]Попытка соеденения с сервером...')
    return BeautifulSoup(response.text, 'lxml')


def get_info(url):
    title_page_soup = get_soup(url)
    title = get_title(title_page_soup)
    get_cover(title_page_soup)
    chapters = get_chapters_tags(url)
    chapters_urls = [chap.get('href') for chap in chapters]
    chapters_names = [' '.join(chap.text.split()[2:]) for chap in chapters]
    return title, chapters_urls[::-1], chapters_names[::-1]


def get_title(soup):
    return soup.find('div', class_='media-name__main').text


def get_cover(soup):
    cover_block = soup.find('div', class_='media-sidebar__cover')
    cover_url = cover_block.find('img').get('src')
    save_cover(cover_url)


def save_cover(url):
    content = requests.get(url, headers=headers).content
    with open('cover.jpg', 'wb') as file:
        file.write(content)


def get_chap_text(url):
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    text = soup.find('div', class_='reader-container').text   
    return chap_text_refinement(text)


def chap_text_refinement(text):
    text = text.replace('***', '\n***\n')
    text = text.replace('\n\n\n', '\n\n')
    return text.replace('\n', '\n\n')


def preparing_book(title):
    with open('book.txt', 'w') as file:
        file.write(f'% {title}\n\n')


def saving_chapter(chapter_name, text):
    with open('book.txt', 'a') as file:
        text = f'# {chapter_name}\n\n' + text + '\n\n'
        file.write(text)


def converting_to_epub():
    print('\n[+]Начало конвертации текста')
    os.system('pandoc book.txt --epub-cover-image=cover.jpg -o book.epub')
    print('[+]Конвертация успешна!\n\n')

def main():
    url = get_url()
    title, chapters_urls, chapters_names = get_info(url)
    preparing_book(title)
    for i in range(len(chapters_urls)):
        print(f'[+]Скачивание главы: {chapters_names[i]}')
        text = get_chap_text('https://ranobelib.me'+chapters_urls[i])
        saving_chapter(chapters_names[i], text)
    converting_to_epub()
    print('\n\nСпасибо за использование программы!')

        

if __name__ == '__main__':
    main()
