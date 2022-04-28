from lib2to3.pgen2 import driver
from requests import options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
from string import punctuation

URL = "https://eldorado.ua"
# options = Options()
# options.add_argument('--headless')
# driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 20)


class EldoradoItems:

    def fix_incapsula(self, url):
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        return soup

    def write_json(self, items_dict, json_file):
        try:
            items_data = json.load(open(json_file))
        except:
            items_data = []

        items_data.append(items_dict)
        
        with open(json_file, 'w') as file:
            json.dump(items_data, file, indent=2, ensure_ascii=False)

    def parse_url(self, url):
        soup = self.fix_incapsula(url)
        categories = soup.find_all('a', {'class': 'menu-item false false'})
        item_counter = 0
        
        for category in categories:
            category_url = URL + category.get('href')
            categories_soup = self.fix_incapsula(category_url)
            items = categories_soup.find('a', {'class': 'show-all-btn'})
            item_url = URL + items.get('href') + '?order=commentsDown'
            items_soup = self.fix_incapsula(item_url)
            products = items_soup.find_all('div', {'class': 'title lp'})
            product_counter = 0
            print(products)
            for product in products:
                items_dict = {}
                json_filename = product.text.encode('ascii', 'ignore').decode().strip().translate({ord(c): None for c in punctuation}).replace(' ', '_')
                json_filename += '.json'
                items_dict['item'] = product.text
                for href in product:
                    product_url = URL + href.get('href')
                    products_soup = self.fix_incapsula(product_url)
                    comment_pagination = products_soup.find_all('div', {'class': 'page-activefalse'})
                    counter_high = int(comment_pagination[0].text)
                    counter_low = 1
                    while counter_low != counter_high:
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="load-more-comments-container"]'))).click()
                        counter_low += 1
                    items_dict['url'] = product_url
                    html = driver.page_source
                    comments_soup = BeautifulSoup(html, 'lxml')
                    comments = comments_soup.find_all('div', {'class': 'comments-field'})
                    for comment in comments:
                        comments_content = comment.find_all('div', {'class': 'comment-content'})
                        for comment_content in comments_content:
                            comments_body = comment_content.find_all('div', {'class': 'comment'})
                            authors_names = comment_content.find_all('div', {'class': 'name'})
                            comments_dates = comment_content.find_all('div', {'class': 'date'})
                            advantages = comment_content.find_all('div', {'class': 'comment-advantages'})
                            disadvantages = comment_content.find_all('div', {'class': 'comment-disadvantages'})
                            rating = comment_content.find_all('span', {'itemprop': 'ratingValue'})
                            # dict для записи 
                            items_dict['author'] = authors_names[0].text
                            items_dict['date'] = comments_dates[0].text
                            items_dict['stars'] = rating[0].text
                            items_dict['comment'] = comments_body[0].text
                            if advantages == []:
                                items_dict['advantage'] = ' '
                            else:
                                items_dict['advantage'] = advantages[0].text[11:]
                            if disadvantages == []:
                                items_dict['disadvantage'] = ' '
                            else:
                                items_dict['disadvantage'] = disadvantages[0].text[10:]
                            self.write_json(items_dict, json_filename)
                product_counter += 1     
                if product_counter == 3:
                    break           
            item_counter += 1
            if item_counter == 3:
                break
             
def main():
    eldorado = EldoradoItems()
    eldorado.parse_url(URL)

if __name__ == '__main__':
    main()
