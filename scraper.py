from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse, re, os, sys, time

class number_of_elements_at_least(object):
  def __init__(self, locator, number):
    self.locator = locator
    self.number = number

  def __call__(self, driver):
    elements = driver.find_elements(*self.locator)
    if len(elements) >= self.number:
        return elements
    else:
        return False

class Scraper(object):

    def __init__(self, headless=False, checkpoint=0, folder='webpages', query='1989 to 2012'):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')

        self.query = query
        self.folder = folder
        self.checkpoint = checkpoint
        self.iterator = range(7,85,4)
        self.pages = 1

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)

        self.driver.get('http://rmrb.egreenapple.com/index2.html')
        self.driver.switch_to_frame('main')

        self.driver.find_element_by_css_selector('input').send_keys(self.query)
        self.driver.find_element_by_id('image1').click()

    def scrape_pages(self):
        while self.checkpoint - self.pages > 14:
            self.skip_pages()
            time.sleep(.100)

        while self.pages <= self.checkpoint:
            self.go_to_next_page()
            time.sleep(.100)

        while True:
            self.save_pages(85)
            self.write_checkpoint()
            self.go_to_next_page()

        self.save_pages(7)

        self.driver.quit()
        sys.exit()

    def save_pages(self, numel):
        i = 0
        while i+1 < len(self.iterator):
            try:
                links = WebDriverWait(self.driver, 10).until(
                    number_of_elements_at_least((By.CSS_SELECTOR, 'td'), numel)
                )
                link = links[self.iterator[i]].find_element_by_css_selector('a')
                i += 1
                if link.text:
                    try:
                        link.click()
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[href="javascript:GoToPDF()"]'))
                        )
                        paragraphs = self.driver.find_elements_by_css_selector('p')
                        fonts = self.driver.find_elements_by_css_selector('font')
                        date = paragraphs[2].text

                        directory = self.get_directory(date)
                        filename = paragraphs[1].text
                        text = fonts[10].text

                        self.write_file(directory, filename, text)

                    finally:
                        self.driver.back()
                        self.driver.switch_to_frame('main')

            except:
                self.driver.quit()
                return

    def get_directory(self, date):
        regex = re.compile('[^0-9]+')
        _, year, month, day, _ = regex.split(date)
        return '/'.join([self.folder,year,month,day])

    def write_checkpoint(self):
        with open(str(self.query) + '.txt', 'wb') as f:
            f.write((str(self.pages)).encode('utf-8'))

    def write_file(self, directory, filename, text):
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(directory + '/' + filename + '.txt', 'wb') as f:
            f.write(text.encode('utf-8'))

    def go_to_next_page(self):
        try:
            imgs = WebDriverWait(self.driver, 10).until(
                number_of_elements_at_least((By.CSS_SELECTOR, '[alt]'), 4)
            )
            next_page = imgs[3]
            next_page.click()
            self.pages += 1

        except:
            self.driver.quit()
            return

    def skip_pages(self):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, '>'))
            )
            button.click()
            self.pages += 15
        except:
            self.driver.quit()
            return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape articles from rmrb.')

    parser.add_argument('--query', default='1989 to 2012', type=str,
        help='the date range to scrape (default: 1989 to 2012)' )
    parser.add_argument('--folder', default='webpages', type=str,
        help='the folder to write downloaded pages to (default: webpages)')
    parser.add_argument('--checkpoint', default='0', type=int,
        help='the last completed page of search results saved (default: 0)')
    parser.add_argument('--headless', action='store_true',
        help='whether to run Chrome in headless mode (default: True)')

    args = parser.parse_args()

    s = Scraper(headless=args.headless, checkpoint=args.checkpoint, folder=args.folder, query=args.query)
    s.scrape_pages()
