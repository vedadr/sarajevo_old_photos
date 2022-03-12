import pickle
import time
import urllib.request as ur
from pathlib import Path

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from random import randint


def get_new_page_number(driver):
    """this will be the generator that returns page links"""
    number_of_pages = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[31]/div[2]/ul/li[8]/a') \
        .text \
        .replace('\nNext', '') \
        .split(' ')[-1]

    number_of_pages = int(number_of_pages)

    for page_nr in range(1, number_of_pages+1):
        yield page_nr


def get_images(driver, downloaded):
    for page_nr in get_new_page_number(driver):

        sleep_time = randint(1, 6)
        print(f'sleeping for {sleep_time}')
        time.sleep(sleep_time)

        if page_nr == 1:
            current_page = driver.find_element_by_xpath("//a[@class='button button-icon-only']")
        else:
            current_page = driver.find_element_by_xpath("(//a[@class='button button-icon-only'])[2]")

            # find_element_by_class_name('sr-only')
        current_page.click()

        time.sleep(5)

        images = driver.find_elements_by_tag_name('img')

        for image in images:
            image_url = image.get_attribute("src")

            print(f'Starting with {image_url}')
            if image_url in downloaded:
                print(f'Skipping {image_url}, already downloaded!')
                continue
            else:
                res = ur.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})

                try:
                    content = ur.urlopen(res).read()
                except Exception as e:
                    """ Skip if any exception occur"""
                    print(f'Exception happened: {e}')

                    downloaded.append(image_url)
                    pickle.dump(downloaded, open('downloaded.pkl', 'wb'))

                    continue

                file_name = 'res/' + image_url.split('/')[-1]\
                    .replace('.php', '')\
                    .replace('?', '')\
                    .replace('=', '')

                try:
                    with open(file_name, 'wb') as handler:
                        handler.write(content)
                except OSError:
                    print(f'Image name {file_name} is not valid, skipping...')

                downloaded.append(image_url)
                pickle.dump(downloaded, open('downloaded.pkl', 'wb'))


if __name__ == '__main__':
    # check if there is a list of already downloaded images
    # go through the new ones and download

    if Path.is_file(Path('downloaded.pkl')):
        downloaded = pickle.load(open('downloaded.pkl', 'rb'))
    else:
        downloaded = []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    driver.get('https://forum.klix.ba/slike-starog-sarajeva-t37595.html')

    get_images(driver, downloaded)

    driver.close()
