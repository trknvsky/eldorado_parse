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

    def get_categories(self, url):
        categories_soup = self.fix_incapsula(url)
        categories = categories_soup.find_all('a', {'class': 'menu-item false false'})
        self.get_products(categories)

    def get_products(self, categories):
        item_counter = 0
        for category in categories:
            category_url = URL + category.get('href')
            categories_soup = self.fix_incapsula(category_url)
            items = categories_soup.find('a', {'class': 'show-all-btn'})
            item_url = URL + items.get('href') + '?order=commentsDown'
            items_soup = self.fix_incapsula(item_url)
            products = items_soup.find_all('div', {'class': 'title lp'})
            items_data = self.get_items(products)
            for item in items_data:
                item_html = item[0]
                item_json_filename = item[1]
                self.get_comments(item_html, item_json_filename)
            item_counter += 1
            if item_counter == 3:
                break

    def get_items(self, products):
        product_counter = 0
        items_data = []
        for product in products:
            items_info = {}
            json_filename = product.text.encode('ascii', 'ignore').decode().strip().translate({ord(c): None for c in punctuation}).replace(' ', '_')
            json_filename += '.json'
            items_info['item'] = product.text
            for href in product:
                product_url = URL + href.get('href')
                products_soup = self.fix_incapsula(product_url)
                prices = products_soup.find_all('div', {'class': 'price'})
                items_info['price'] = prices[0].text
                characteristics = products_soup.find_all('ul', {'class': 'product-small-description'})
                if characteristics == []:
                    characteristics = products_soup.find_all('ul', {'class': 'general-characteristic'})
                item_characteristics = ''
                for characteristic in characteristics[0]:
                    item_characteristics += characteristic.text + '; '
                items_info['characteristics'] = item_characteristics                
                comment_pagination = products_soup.find_all('div', {'class': 'page-activefalse'})
                counter_high = int(comment_pagination[0].text)
                counter_low = 1
                while counter_low != counter_high:
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="load-more-comments-container"]'))).click()
                    counter_low += 1
                items_info['url'] = product_url
                self.write_json(items_info, json_filename)
                html = driver.page_source
                items_data.append([html, json_filename])
            product_counter += 1     
            if product_counter == 3:
                break  
        return items_data

    def get_comments(self, html, json_filename):
        items_dict = {}
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
          
def main():
    eldorado = EldoradoItems()
    eldorado.get_categories(URL)

if __name__ == '__main__':
    main()
