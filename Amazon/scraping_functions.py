import re
from urllib.parse import urljoin
from unidecode import unidecode
import time
from bs4 import BeautifulSoup
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

class Helper:

    def remove_non_numeric(self, s):
        return "".join(c for c in s if c.isnumeric())

    def node_arr(node_str):
        numbers = re.findall(r'\b\d{9,}\b', node_str)
        if numbers:
            array = list(map(int, numbers))
            return array
        else:
            return None

class GoogleSheetsAuth:
    def __init__(self, credentials_file, scope):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file)
        self.gc = gspread.authorize(self.credentials)

    def open_sheet(self, sheet_name, worksheet_name):
        sheet = self.gc.open(sheet_name).worksheet(worksheet_name)
        return sheet 

class WebDriverManager:
    def __init__(self, headless=True):
        options = Options()
        options.headless = headless
        self.driver = webdriver.Firefox(options=options)
    
    def get_driver(self):
        return self.driver


class AmazonScraper:

    def __init__(self, soup, helper, driver):
        self.soup = soup
        self.helper = helper
        self.driver = driver

    def regex_best_seller_rank(self):
        regex = r'#\d+ in Books \('
        regex1 = r'#\d+,\d+ in Books \('
        regex2 = r'#\d+,\d+,\d+ in Books \('
        regex3 = r'#\d+,\d+,\d+,\d+ in Books \('
        
        soup = self.soup

        rank_match = re.search(regex, soup.text)
        if rank_match == None:
            rank_match = re.search(regex1, soup.text)
            if rank_match == None:
                rank_match = re.search(regex2, soup.text)
                if rank_match == None:
                    rank_match = re.search(regex3, soup.text)

        if rank_match:
            return int(self.helper.remove_non_numeric(rank_match.group()))
        else:
            return None
    
    def rating(self):
        soup = self.soup
        rating = soup.find("span", id="acrCustomerReviewText")
        if rating:
            rating = "".join(rating.stripped_strings)
            return self.helper.remove_non_numeric(rating)
        else:
            return None
    
    def find_title(self):
        soup = self.soup
        title = soup.find("span", id="productTitle")
        if title:
            return "".join(title.stripped_strings)
        else:
            return None
        
    def stars(self):
        soup = self.soup
        star = soup.select_one('span[data-hook="rating-out-of-text"]')
        if star:
            if star.get_text():
                return float(star.get_text().split()[0])
            else:
                return None
        else:
            return None

    def sellers_list(self):
        soup = self.soup
        url = "https://amazon.in"
        sellers = []
        i = 0
        j = 0

        def seller_price(i):
            seller_num_id = "aod-price-" + str(i)
            price_div = soup.find("span", id=seller_num_id)
            if price_div:
                price = price_div.find_all('span')
                if len(price) > 1:
                    # grab text from 1st child span tag
                    # if it contains % then it is a discount
                    if "%" in price[0].text:
                        discount = float(price[0].text.strip("%"))
                    else:
                        discount = None
                    
                    if discount is None:
                        price = price[0].find('span').text.strip("₹")
                        if price is not None:
                            price = price.replace(",", "")
                            price = float(price)
                        else:
                            price = None
                    else:
                        price = price[1].find('span').text.strip("₹")
                        if price is not None:
                            price = price.replace(",", "")
                            price = float(price)
                    return [price, discount]
                else:
                    return None
            else:
                return None
            
        divs = soup.find_all("div", id="aod-offer-soldBy")
        if divs:
            for div in divs:
                child_divs = div.find_all("div")[0].find_all("div")[2]
                seller_link = urljoin(url, child_divs.find("a").get("href"))
                seller_id = re.search(r'(seller=(.*?))&',
                                    seller_link).group(1).split("=")[1]
                seller_name = unidecode(child_divs.find('a').text.strip())
                prime_status = int(
                    re.search(r'(isAmazonFulfilled=(.*?))&', seller_link).group(1).split("=")[1])
                seller_star = child_divs.find("i")
                if seller_star:
                    seller_star = float(seller_star.get("class")[2].strip(
                        'a-star-mini-').replace('-', '.'))
                price = seller_price(i)[0]
                discount = seller_price(i)[1]
                j += 1
                if i == 0:
                    buy_box_status = True
                else:
                    buy_box_status = False
                if j == 1:
                    i = 0
                else:
                    i += 1
                seller_rating = re.search(r'\((.*?) rating', child_divs.text)
                if seller_rating:
                    seller_rating = int(self.helper.remove_non_numeric(seller_rating.group(1)))
                elif re.search(r'\((.*?) ratings', child_divs.text):
                    seller_rating = int(self.helper.remove_non_numeric(
                        re.search(r'\((.*?) ratings', child_divs.text).group(1)))
                else:
                    seller_rating = None
                sellers.append([seller_id, seller_name, seller_rating, seller_star,
                            prime_status, seller_link, price, buy_box_status, discount])
            return sellers
        else:
            return [[None, None, None, None, None, None, None, None, None]]

    def seller_nos(self):
        soup = self.soup
        seller_count = soup.find("span", id="aod-filter-offer-count-string")
        if seller_count:
            if seller_count.text != "Currently, there are no other sellers matching your location and / or item specification. Try updating the filters or your location to find additional sellers.":
                return int(self.helper.remove_non_numeric(seller_count.text)) + 1
            else:
                return 1
        else:
            return 0


    def buy_box_seller(self):
        soup = self.soup
        div = soup.find("div", id="merchant-info")
        if div:
            seller = div.find_all("a")[0]
            if seller:
                if seller.find("span"):
                    return seller.find("span").text
                else:
                    return seller.text
            else:
                return None
        else:
            return None
        
    def sub_category_rank(self):
        soup = self.soup
        regex = r' #\d+ in '
        regex1 = r' #\d+,\d+ in '
        regex2 = r' #\d+,\d+,\d+ in '
        regex3 = r' #\d+,\d+,\d+,\d+ in '

        sub_rank = []
        for expression in [regex, regex1, regex2, regex3]:
            sub_rank_match = re.finditer(expression, soup.text)
            if sub_rank_match:
                for match in sub_rank_match:
                    text_node = soup.find(
                        text=soup.text[match.start():match.end()])
                    if text_node:
                        span_element = text_node.parent
                        a_tag = span_element.find("a").get("href")
                        node = re.search(r'\d+', a_tag).group()
                        category_name = span_element.find("a").text
                        rank = self.helper.remove_non_numeric(match.group()[0:])
                        sub_rank.append([node, category_name, rank])
                    else:
                        continue
            continue
        if not sub_rank:
            sub_rank.append([None, None, None])
        return sub_rank

    def sub_ranks_string(self, category_rank):
        sub_rank_string = ""
        if category_rank[0][0] == None:
            return None
        for sub_rank in category_rank:
            sub_rank_string = sub_rank_string + \
                sub_rank[1] + " - " + sub_rank[2] + "\n"
        return sub_rank_string

    def mrp_price(self):
        soup = self.soup
        mrp_price = soup.find("span", id="listPrice")
        if mrp_price:
            return float((mrp_price.text)[1:].replace(",", ""))
        else:
            return None


    def selling_price(self):
        soup = self.soup
        price_div = soup.find("span", id="price")
        if price_div:
            price = price_div.text.strip("₹")
            price = price.replace(",", "")
            return float(price)

    def list_discount(self):
        soup = self.soup
        list_discount = soup.find("span", id="savingsPercentage")
        if list_discount:
            strin_discount = list_discount.text.strip("(").strip(")").strip("%")
            return float(strin_discount)
        else:
            return None


    def written_reviews(self, asin):
        driver = self.driver
        url = "https://amazon.in/product-reviews/" + asin
        # handle error if internt is not connected
        driver.get(url)
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        regex = r'(\d+ with reviews)'
        if regex:
            if re.search(regex, soup.text):
                return int(self.helper.remove_non_numeric(re.search(regex, soup.text).group()))
            # return int(remove_non_numeric(re.search(regex, soup.text).group()))
        else:
            return None


    def suppressed_asin(self, asin):
        driver = self.driver
        search = driver.find_element(By.ID, "twotabsearchtextbox")
        search.send_keys(asin)
        search.send_keys(Keys.RETURN)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # check = soup.find("div", {"cel_widget_id": "MAIN-SEARCH_RESULTS-1"})
        check = soup.find("div", {"data-asin": str(asin)})
        if check:
            return False
        else:
            return True
    
    def no_of_pages(self):
        soup = self.soup
        feautures_div = soup.find("div", id="detailBullets_feature_div")
        pages_num_regex = r'(\d+ pages)'
        if feautures_div:
            if re.search(pages_num_regex, feautures_div.text):
                return int(self.helper.remove_non_numeric(re.search(pages_num_regex, feautures_div.text).group()))
            else:
                return None
        else:
            return None


    def get_weight(self):
        soup = self.soup
        feautures_div = soup.find("div", id="detailBullets_feature_div")
        weight_regex = r'(\d+ g)'
        if feautures_div:
            if re.search(weight_regex, feautures_div.text):
                return re.search(weight_regex, feautures_div.text).group().strip("g")
            else:
                return None
        else:
            return None

    def get_dimensions(self):
        soup = self.soup
        feautures_div = soup.find("div", id="detailBullets_feature_div")
        dimensions_regex = r'(\d+ x \d+ x \d+ cm)'
        if feautures_div:
            if re.search(dimensions_regex, feautures_div.text):
                return re.search(dimensions_regex, feautures_div.text).group()
            else:
                return None
        else:
            return None

    def get_a_plus_page(self):
        soup = self.soup
        page = soup.find('div', id='aplus_feature_div')
        if page:
            img = page.find('img')
            if img:
                return img.get('data-src')
            else:
                return None
        else:
            return None


    def get_description(self):
        soup = self.soup
        desc = soup.find('div', id='bookDescription_feature_div')
        if desc:
            if desc.text:
                return desc.text.strip()
            else:
                return None
        else:
            return None

    def get_title_image2(self):
        soup = self.soup
        img_canvas = soup.find('img', id="imgBlkFront")
        if img_canvas:
            return img_canvas.get('src')
        else:
            return None

    def get_subtitle(self):
        soup = self.soup
        subtitle = soup.find('span', id='productSubtitle')
        if subtitle:
            return subtitle.text.strip()
        else:
            return None


    def kindle_version(self):
        soup = self.soup
        kindle_version = soup.find("span", {"id": "kcpAppsPopOver-wrapper"})
        if kindle_version:
            return True
        else:
            return False


   