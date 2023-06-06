import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.firefox.options import Options
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
from urllib.parse import urljoin
from datetime import datetime
import json
from unidecode import unidecode
from pandas import DataFrame as df
import random
import os
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback


def log_error(error_message):
    filename = "error.log"
    try:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")
        with open(filename, "a") as f:
            f.write(error_message + "\n")
    except Exception as e:
        # Handle the exception here, for example, by printing the error message
        print("Error logging the error:", str(e))


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials/amazon-credentials.json', scope)
gc = gspread.authorize(credentials)

write_credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials/credentials.json', scope)
write_client = gspread.authorize(write_credentials)

examcart_sheet = gc.open(
    'Up coming and Active Projects').worksheet("AUDIT + CAMPAIGN 2")
educart_sheet = gc.open('Up coming and Active Projects').worksheet("Educart")

examcart_row_count = examcart_sheet.row_count
educart_row_count = educart_sheet.row_count

examcart_range = examcart_sheet.get("A459:Q" + str(examcart_row_count))
educart_range = educart_sheet.get("A2:Q" + str(educart_row_count))

all_asins =   examcart_range + educart_range

# product_sheet = gc.open('Up coming and Active Projects').worksheet("Products Data")
# sellers_sheet = gc.open('Up coming and Active Projects').worksheet("Sellers Data")
# subrank_sheet = gc.open('Up coming and Active Projects').worksheet("Amazon Subrank")
# review_sheet = gc.open('Up coming and Active Projects').worksheet("Reviews")
# adc_node_sheet = gc.open('Up coming and Active Projects').worksheet("Adc Subrank")
# all_priority_sellers_sheet = gc.open('Up coming and Active Projects').worksheet("Priority Sellers")

read_status = False

while read_status == False:
    try:
        product_sheet = write_client.open('Amazon').worksheet("Products Data")
        sellers_sheet = write_client.open('Amazon').worksheet("Sellers Data")
        subrank_sheet = write_client.open('Amazon').worksheet("Amazon Subrank")
        review_sheet = write_client.open('Amazon').worksheet("Reviews")
        adc_node_sheet = write_client.open('Amazon').worksheet("Adc Subrank")
        all_priority_sellers_sheet = write_client.open('Amazon').worksheet("Priority Sellers")
        read_status = True
    except Exception as e:
        log_error("Error in reading the sheets: " + str(e))
        print("Error in reading the sheets: " + str(e))
        time.sleep(60)
        continue


options = Options()
options.headless = True


def remove_non_numeric(s):
    return "".join(c for c in s if c.isnumeric())


def node_arr(node_str):
    numbers = re.findall(r'\b\d{9,}\b', node_str)
    if numbers:
        array = list(map(int, numbers))
        return array
    else:
        return None


def regex_best_seller_rank(soup):
    regex = r'#\d+ in Books \('
    regex1 = r'#\d+,\d+ in Books \('
    regex2 = r'#\d+,\d+,\d+ in Books \('
    regex3 = r'#\d+,\d+,\d+,\d+ in Books \('

    rank_match = re.search(regex, soup.text)
    if rank_match == None:
        rank_match = re.search(regex1, soup.text)
        if rank_match == None:
            rank_match = re.search(regex2, soup.text)
            if rank_match == None:
                rank_match = re.search(regex3, soup.text)

    if rank_match:
        return int(remove_non_numeric(rank_match.group()))
    else:
        return None


def rating(soup):
    rating = soup.find("span", id="acrCustomerReviewText")
    if rating:
        rating = "".join(rating.stripped_strings)
        return remove_non_numeric(rating)
    else:
        return None


def find_title(soup):
    title = soup.find("span", id="productTitle")
    if title:
        return "".join(title.stripped_strings)
    else:
        return None


def stars(soup):
    star = soup.select_one('span[data-hook="rating-out-of-text"]')
    if star:
        if star.get_text():
            return float(star.get_text().split()[0])
        else:
            return None
    else:
        return None


def sellers_list(soup):
    url = "https://amazon.in"
    sellers = []
    i = 0
    j = 0

    def seller_price(i):
        seller_num_id = "aod-price-" + str(i)
        price_div = soup.find("div", id=seller_num_id)
        if price_div:
            price = price_div.find('span')
            if price:
                # grab text from 1st child span tag
                price = price.find('span').text.strip("₹")
                price = price.replace(",", "")
                price = float(price)
                return price
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
            price = seller_price(i)
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
                seller_rating = int(remove_non_numeric(seller_rating.group(1)))
            elif re.search(r'\((.*?) ratings', child_divs.text):
                seller_rating = int(remove_non_numeric(
                    re.search(r'\((.*?) ratings', child_divs.text).group(1)))
            else:
                seller_rating = None
            sellers.append([seller_id, seller_name, seller_rating, seller_star,
                           prime_status, seller_link, price, buy_box_status])
        return sellers
    else:
        return [[None, None, None, None, None, None, None, None]]


def seller_nos(soup):
    seller_count = soup.find("span", id="aod-filter-offer-count-string")
    if seller_count:
        if seller_count.text != "Currently, there are no other sellers matching your location and / or item specification. Try updating the filters or your location to find additional sellers.":
            return int(remove_non_numeric(seller_count.text)) + 1
        else:
            return 1
    else:
        return 0


def buy_box_seller(soup):
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

# def sub_category_rank_old(soup):
#     regex = r' #\d+ in '
#     regex1 = r' #\d+,\d+ in '
#     regex2 = r' #\d+,\d+,\d+ in '
#     regex3 = r' #\d+,\d+,\d+,\d+ in '

#     sub_rank = []

#     for expression in [regex, regex1, regex2, regex3]:
#         sub_rank_match = re.finditer(expression, soup.text)
#         if sub_rank_match:
#             for match in sub_rank_match:
#                 text_node = soup.find(text=soup.text[match.start():match.end()])
#                 if text_node:
#                     span_element = text_node.parent
#                     a_tag = span_element.find("a").get("href")
#                     node = re.search(r'\d+', a_tag).group()
#                     category_name = span_element.find("a").text
#                     rank = remove_non_numeric(match.group()[0:])
#                     sub_rank.append([node, category_name, rank])
#                 else:
#                     continue
#             return sub_rank
#         else:
#             return [[None, None, None]]


def sub_category_rank(soup):
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
                    rank = remove_non_numeric(match.group()[0:])
                    sub_rank.append([node, category_name, rank])
                else:
                    continue
        continue
    if not sub_rank:
        sub_rank.append([None, None, None])
    return sub_rank


def sub_ranks_string(category_rank):
    sub_rank_string = ""
    if category_rank[0][0] == None:
        return None
    for sub_rank in category_rank:
        sub_rank_string = sub_rank_string + \
            sub_rank[1] + " - " + sub_rank[2] + "\n"
    return sub_rank_string


def mrp_price(soup):
    mrp_price = soup.find("span", id="listPrice")
    if mrp_price:
        return float((mrp_price.text)[1:].replace(",", ""))
    else:
        return None


def selling_price(soup):
    price_div = soup.find("span", id="price")
    if price_div:
        price = price_div.text.strip("₹")
        price = price.replace(",", "")
        return float(price)


def list_discount(soup):
    list_discount = soup.find("span", id="savingsPercentage")
    if list_discount:
        strin_discount = list_discount.text.strip("(").strip(")").strip("%")
        return float(strin_discount)
    else:
        return None


def written_reviews(asin):
    url = "https://amazon.in/product-reviews/" + asin
    # handle error if internt is not connected
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    regex = r'(\d+ with reviews)'
    if regex:
        if re.search(regex, soup.text):
            return int(remove_non_numeric(re.search(regex, soup.text).group()))
        # return int(remove_non_numeric(re.search(regex, soup.text).group()))
    else:
        return None


def suppressed_asin(asin):
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

    regex1 = r'(\d+ result for)'
    regex2 = r'(\d+ results for)'
    if re.search(regex1, soup.text):
        if int(remove_non_numeric(re.search(regex1, soup.text).group())) == 0:
            return True
        else:
            return False

    elif re.search(regex2, soup.text):
        if int(remove_non_numeric(re.search(regex2, soup.text).group())) == 0:
            return True
        else:
            return False
    else:
        return True


def no_of_pages(soup):
    feautures_div = soup.find("div", id="detailBullets_feature_div")
    pages_num_regex = r'(\d+ pages)'
    if feautures_div:
        if re.search(pages_num_regex, feautures_div.text):
            return int(remove_non_numeric(re.search(pages_num_regex, feautures_div.text).group()))
        else:
            return None
    else:
        return None


def get_weight(soup):
    feautures_div = soup.find("div", id="detailBullets_feature_div")
    weight_regex = r'(\d+ g)'
    if feautures_div:
        if re.search(weight_regex, feautures_div.text):
            return re.search(weight_regex, feautures_div.text).group().strip("g")
        else:
            return None
    else:
        return None


def get_dimensions(soup):
    feautures_div = soup.find("div", id="detailBullets_feature_div")
    dimensions_regex = r'(\d+ x \d+ x \d+ cm)'
    if feautures_div:
        if re.search(dimensions_regex, feautures_div.text):
            return re.search(dimensions_regex, feautures_div.text).group()
        else:
            return None
    else:
        return None


def get_a_plus_page(soup):
    page = soup.find('div', id='aplus_feature_div')
    if page:
        img = page.find('img')
        if img:
            return img.get('data-src')
        else:
            return None
    else:
        return None


def get_description(soup):
    desc = soup.find('div', id='bookDescription_feature_div')
    if desc:
        if desc.text:
            return desc.text.strip()
        else:
            return None
    else:
        return None

# def get_title_image_old(soup):
#     img_canvas = soup.find('div', id = "booksImageBlock_feature_div")
#     if img_canvas:
#         img_canvas = img_canvas.find('img')
#         if img_canvas:
#             return img_canvas.get('src')
#         else:
#             return None
#     else:
#         return None


def get_title_image2(soup):
    img_canvas = soup.find('img', id="imgBlkFront")
    if img_canvas:
        return img_canvas.get('src')
    else:
        return None


# def final_array(asin):
    url = "https://amazon.in/product-reviews/" + asin
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    all_review_data = []

    pf_list = []
    rv_list = []

    def review_data():
        profiles = soup.find_all('span', {'class': 'a-profile-name'})
        reviews = soup.find_all('span', {'data-hook': 'review-body'})
        if profiles:
            for profile in profiles:
                pf_list.append(profile.text)
        if reviews:
            for rev in reviews:
                rv_list.append(rev.text)
        for i in range(len(pf_list)):
            all_review_data.append([asin, pf_list[i], rv_list[i]])
        return all_review_data

    # execute for 1st page
    review_data()

    next_page = soup.find('li', {'class': 'a-last'})
    if next_page:
        next_page = soup.find('li', {'class': 'a-last'}).find('a')
        if next_page:
            while next_page:
                time.sleep(0.5)
                next_page = soup.find('li', {'class': 'a-last'}).find('a')
                if next_page == None:
                    break
                time.sleep(random.randint(1, 3))
                next_page_element = driver.find_element(
                    By.XPATH, "//a[@href='" + next_page["href"] + "']")
                driver.execute_script(
                    "arguments[0].scrollIntoView();", next_page_element)
                ActionChains(driver).move_to_element(
                    next_page_element).click(next_page_element).perform()
                time.sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                review_data()
                next_page = soup.find('li', {'class': 'a-last'})

    return all_review_data


def get_subtitle(soup):
    subtitle = soup.find('span', id='productSubtitle')
    if subtitle:
        return subtitle.text.strip()
    else:
        return None


def kindle_version(soup):
    kindle_version = soup.find("span", {"id": "kcpAppsPopOver-wrapper"})
    if kindle_version:
        return True
    else:
        return False


def load_other_metrics():
    if os.path.exists("other_metrics.json"):
        with open("other_metrics.json", "r") as f:
            other_metrics = json.load(f)
            return other_metrics
    else:
        asin_metric = {}
        return asin_metric


def fetch_other_metrics(asin, best_seller_rank, date):
    other_metrics = load_other_metrics()
    if asin in other_metrics:
        prev_category = other_metrics[asin]["prev_category_rank"]

        if best_seller_rank == None:
            atb_rank = other_metrics[asin]["atb_rank"]
            atb_date = other_metrics[asin]["atb_date"]
        else:
            if other_metrics[asin]["atb_rank"] == None:
                atb_rank = best_seller_rank
                atb_date = date
            else:
                if best_seller_rank > other_metrics[asin]["atb_rank"]:
                    atb_rank = other_metrics[asin]["atb_rank"]
                    atb_date = other_metrics[asin]["atb_date"]
                else:
                    atb_rank = best_seller_rank
                    atb_date = date
        return prev_category, atb_rank, atb_date
    else:
        return None, None, None


def save_other_metrics(asin, sub_category_string, best_seller_rank, date):
    other_metrics = load_other_metrics()

    if asin not in other_metrics:
        other_metrics[asin] = {}
        other_metrics[asin]["prev_category_rank"] = sub_category_string
        other_metrics[asin]["atb_rank"] = best_seller_rank
        other_metrics[asin]["atb_date"] = date
    else:
        other_metrics[asin]["prev_category_rank"] = sub_category_string

        if best_seller_rank == None:
            other_metrics[asin]["atb_rank"] = other_metrics[asin]["atb_rank"]
            other_metrics[asin]["atb_date"] = other_metrics[asin]["atb_date"]
        else:
            if other_metrics[asin]["atb_rank"] == None:
                other_metrics[asin]["atb_rank"] = best_seller_rank
                other_metrics[asin]["atb_date"] = date
            else:
                if best_seller_rank < other_metrics[asin]["atb_rank"]:
                    other_metrics[asin]["atb_rank"] = best_seller_rank
                    other_metrics[asin]["atb_date"] = date

    with open("other_metrics.json", "w") as f:
        json.dump(other_metrics, f)


# def load_other_metrics():
#     if os.path.exists("other_metrics.json"):
#         with open("other_metrics.json", "r") as f:
#             other_metrics = json.load(f)
#             return other_metrics
#     else:
#         asin_metric = {}
#         return asin_metric
# This is the test comment
## def fetch_other_metrics(asin, best_seller_rank, date):
#     other_metrics = load_other_metrics()
#     if asin in other_metrics:
#         prev_category = other_metrics[asin]["prev_category_rank"]
#         if best_seller_rank > other_metrics[asin]["atb_rank"]:
#             atb_rank = other_metrics[asin]["atb_rank"]
#             atb_date = other_metrics[asin]["atb_date"]
#         else:
#             atb_rank = best_seller_rank
#             atb_date = date
#         return prev_category, atb_rank, atb_date
#     else:
#         return None, None, None

# def save_other_metrics(asin, sub_category_string, best_seller_rank, date):
#     other_metrics = load_other_metrics()

#     if asin not in other_metrics:
#         other_metrics[asin] = {}
#         other_metrics[asin]["prev_category_rank"] = sub_category_string
#         other_metrics[asin]["atb_rank"] = best_seller_rank
#         other_metrics[asin]["atb_date"] = date
#     else:
#         other_metrics[asin]["prev_category_rank"] = sub_category_string
#         if best_seller_rank < other_metrics[asin]["atb_rank"]:
#             other_metrics[asin]["atb_rank"] = best_seller_rank
#             other_metrics[asin]["atb_date"] = date

#     with open("other_metrics.json", "w") as f:
#         json.dump(other_metrics, f)
product_array2 = []
for Asin in all_asins:
    # error handling for no internt connection
    driver = webdriver.Firefox(options=options)
    attempts = 0
    success = False
    while not success or attempts < 5:
        try:
            if ((Asin[6] == ("Active & Starred")) or (Asin[6] == ("Active"))) and (Asin[7]):
                asin = Asin[7]
                url = "https://amazon.in/dp/" + asin
                driver.get(url)
                time.sleep(5)

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                old_link = soup.find("span", class_="olp-new olp-link")
                old_link = soup.find("span", id="olp-consolidated-text")
                if True:
                    print("old link found")
                    # old_link = old_link.find("span").find("a")
                    # old_link = old_link.get("href")
                    old_link = '/gp/offer-listing/' + asin + '/ref=tmm_pap_new_olp_0?ie=UTF8&condition=new'
                    old_link = "https://www.amazon.in" + old_link
                    driver.get(old_link)
                    time.sleep(5)
                    driver.execute_script(
                        'return window.scrollTo(0, document.body.scrollHeight);')
                    wait = WebDriverWait(driver, 10)

                    time.sleep(2)
                    attempts2 = 0
                    while attempts2 < 5:
                        try:
                            wait.until(EC.presence_of_element_located(
                                (By.ID, "all-offers-display-scroller")))
                            div_element = driver.find_element(
                                By.ID, "all-offers-display-scroller")
                            driver.execute_script(
                                "arguments[0].scrollTop = 7000", div_element)
                            break
                        except:
                            attempts2 += 1
                            time.sleep(5)
                            driver.execute_script(
                                'return window.scrollTo(0, document.body.scrollHeight);')
                            print("Scrolling")
                            continue

                time.sleep(3)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                date = datetime.now().strftime("%d-%m-%Y")
                amzn_title = find_title(soup)
                best_seller_rank = regex_best_seller_rank(soup)
                ratings = rating(soup)
                star = stars(soup)
                seller_count = seller_nos(soup)
                main_seller = buy_box_seller(soup)
                main_seller_mrp = mrp_price(soup)
                main_seller_discount = list_discount(soup)
                main_seller_price = selling_price(soup)
                review_count = written_reviews(asin)
                # profiles_with_reviews = final_array(asin)
                is_asin_suppressed = suppressed_asin(asin)
                category_rank = sub_category_rank(soup)
                sub_category_string = sub_ranks_string(category_rank)
                sellers = sellers_list(soup)
                pages = no_of_pages(soup)
                weight = get_weight(soup)
                dimensions = get_dimensions(soup)
                a_plus = get_a_plus_page(soup)
                description = get_description(soup)
                # title_img = get_title_image(soup)
                title_img = get_title_image2(soup)
                subtitle = get_subtitle(soup)
                kindle = kindle_version(soup)

                company_name = Asin[0]
                book_img = Asin[1]
                book_code = Asin[2]
                book_price = Asin[4]
                book_title = Asin[5]
                category_list = Asin[9] # J
                book_status = Asin[6]

                book_sub_tag = Asin[12] # M
                book_key_tag = Asin[13] # N
                book_type = Asin[14]    # O
                try: 
                    book_description = Asin[15]
                except:
                    book_description = ""
               
                prev_category_rank_string, atb_rank, atb_date = fetch_other_metrics(
                    asin, best_seller_rank, date)
                save_other_metrics(asin, sub_category_string,
                                   best_seller_rank, date)

                if prev_category_rank_string == None:
                    prev_category_rank_string = sub_category_string
                if atb_rank == None:
                    atb_rank = best_seller_rank
                if atb_date == None:
                    atb_date = date

                product_array1 = [date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_category_string, pages,
                                  weight, dimensions, a_plus, description, title_img, kindle, company_name, book_img, book_code, book_price, book_title, category_list, book_status, prev_category_rank_string, atb_rank, atb_date, book_key_tag, subtitle, book_description, book_sub_tag, book_type]
                product_array2.append(product_array1)
                print(product_array1)

                seller_array1 = []
                for seller in sellers:
                    seller_array2 = [date, asin, seller[0], seller[1], seller[2], seller[3], seller[4], seller[5], seller[6],
                                     seller[7], company_name, book_img, book_code, book_price, book_title, book_status, book_key_tag, book_sub_tag, book_type]
                    seller_array1.append(seller_array2)
                print(seller_array1)

                sub_rank1 = []
                for sub_rank in category_rank:
                    sub_rank2 = [date, asin, sub_rank[0], sub_rank[1], sub_rank[2], company_name,
                                 book_img, book_code, book_price, book_title, category_list, book_status]
                    sub_rank1.append(sub_rank2)
                subrank_sheet.append_rows(sub_rank1)
                sellers_sheet.append_rows(seller_array1)
                product_sheet.append_rows([product_array1])
                # review_sheet.append_rows(profiles_with_reviews)
                df = pandas.DataFrame([product_array1])
                df.to_csv('hope.csv', mode='a', header=False, index=False)

                success = True
                attempts= 5

            else:
                print(Asin[6])
                print("Not active")
                attempts= 5
                success = True
       	    driver.close()
        except Exception as e:
            print("Error occured")
            tb_str = traceback.format_tb(e.__traceback__)[0]
            error = f"{e.__class__.__name__}: {e} on line {tb_str.split(',')[1].lstrip().split(' ')[1]}" + \
                f"{asin}"
            print(error)

            try:
                DiscordWebhook(
                    url="https://discord.com/api/webhooks/1075110571193663589/F8R0zj0yhtsNVzcafVWTavpuIG2Q2DPQoKLG9JmiCZIscoomUVIm6sdGIk3hZlrXwd3b", content=f"{error}").execute()
            except Exception as e:
                print((e))
            print(e)
            time.sleep(10)
            attempts += 1
            if attempts > 5:
                success = True
                break
            driver.close()
            continue
product_sheet.append_rows(product_array2)
DiscordWebhook(url="https://discord.com/api/webhooks/1075110571193663589/F8R0zj0yhtsNVzcafVWTavpuIG2Q2DPQoKLG9JmiCZIscoomUVIm6sdGIk3hZlrXwd3b",
               content=f" Amazon Date Updated").execute()
