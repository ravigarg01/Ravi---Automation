import mysql.connector
import pyodbc
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

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('D:\Ravi_projects\Scraping\credentials\credentials.json', scope)
gc = gspread.authorize(credentials)

# connect = mysql.connector.connect(user = 'root', password = "R@vig@rg1907", host = 'localhost', database = 'amazon')
connect = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
'Server=Ravi-Digital-PC\SQLEXPRESS;'
'Database=amazon;''Trusted_Connection=yes;')
cursor = connect.cursor()

sheetname = "Amazon Ranks"
sheet = gc.open("products").worksheet(sheetname)
range = sheet.get("A2:B36")

master_sheet = gc.open("products").worksheet("master")
category_rank_sheet = gc.open("products").worksheet("category_rank")
amzn_sellers_sheet = gc.open("products").worksheet("amzn_sellers")


for row in range:
    asin = row[0]
    status = row[1]
    cursor.execute("IF NOT EXISTS (SELECT * FROM asin_status WHERE asin = ?) BEGIN INSERT INTO asin_status (asin, status) VALUES (?, ?) END ELSE BEGIN UPDATE asin_status SET status = ? WHERE asin = ? END", (asin, asin, status, status, asin))
    connect.commit()

options = webdriver.FirefoxOptions()
options.headless = False

capabilities = DesiredCapabilities.FIREFOX.copy()
capabilities['acceptSslCerts'] = True
capabilities['acceptInsecureCerts'] = True
capabilities['acceptLanguage'] = 'en-US'
capabilities['userAgent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'

driver = webdriver.Firefox(options=options)

def remove_non_numeric(s):
    return "".join(c for c in s if c.isnumeric())

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
    rating = soup.find("span",id="acrCustomerReviewText")
    if rating:
        rating = "".join(rating.stripped_strings)
        return remove_non_numeric(rating)
    else:
        return None

def find_title(soup):
    title = soup.find("span", id= "productTitle")
    if title:
        return "".join(title.stripped_strings)
    else:
        return None

def stars(soup):
    star = soup.select_one('span[data-hook="rating-out-of-text"]')
    if star:
        return float(star.get_text().split()[0])
    else:
        return None

def sellers_list(soup):
    url = "https://amazon.in"
    sellers = []
    i = 0; j = 0
    def seller_price(i):
        seller_num_id = "aod-price-" + str(i)
        price_div = soup.find("div", id = seller_num_id)
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
    
    divs = soup.find_all("div", id = "aod-offer-soldBy")
    #print no of divs
    if divs:
        for div in divs:
            child_divs = div.find_all("div")[0].find_all("div")[2]
            seller_link = urljoin(url, child_divs.find("a").get("href"))
            seller_id = re.search(r'(seller=(.*?))&', seller_link).group(1).split("=")[1]
            print("below is the seller id")
            print(seller_id)
            seller_name = unidecode(child_divs.find('a').text.strip())
            prime_status = int(re.search(r'(isAmazonFulfilled=(.*?))&', seller_link).group(1).split("=")[1])
            seller_star = float(child_divs.find("i").get("class")[2].strip('a-star-mini-').replace('-', '.'))
            price = seller_price(i); j += 1
            if i ==0:
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
                seller_rating = int(remove_non_numeric(re.search(r'\((.*?) ratings', child_divs.text).group(1)))
            else:
                seller_rating = None
            sellers.append([seller_id, seller_name, seller_rating, seller_star, prime_status, seller_link, price, buy_box_status])
        return sellers
    else:
        return [[None, None, None, None, None, None, None, None]]
    
def seller_nos(soup):
    seller_count = soup.find("span", id = "aod-filter-offer-count-string")
    if seller_count:
        if seller_count.text != "Currently, there are no other sellers matching your location and / or item specification. Try updating the filters or your location to find additional sellers.":
            return int(remove_non_numeric(seller_count.text))
        else :
            return 1
    else:
        return 0

def buy_box_seller (soup):
    div = soup.find("div", id = "merchant-info")
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
                text_node = soup.find(text=soup.text[match.start():match.end()])
                span_element = text_node.parent
                a_tag = span_element.find("a").get("href")
                node = re.search(r'\d+', a_tag).group()
                category_name = span_element.find("a").text
                rank = remove_non_numeric(match.group()[0:])
                sub_rank.append([node, category_name, rank])
            return sub_rank
        else:
            return [[None, None, None]]

def list_price(soup): 
    list_price = soup.find("span", id = "listPrice")
    if list_price:
        return float((list_price.text)[1:].replace(",", ""))
    else:
        return None

def selling_price(soup):
    price_div = soup.find("div", id = "price")
    if price_div:
        price = price_div.text.strip("₹")
        price = price.replace(",", "")
        return float(price)

def list_discount(soup):
    list_discount = soup.find("span", id = "savingsPercentage")
    if list_discount:
        strin_discount = list_discount.text.strip("(").strip(")").strip("%")
        return float(strin_discount)
    else:
        return None

def written_reviews(soup):
    url = "https://amazon.in/product-reviews/" + asin
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    regex = r'(\d+ with reviews)'
    if regex:
        return int(remove_non_numeric(re.search(regex, soup.text).group()))
    else:
        return None

def suppressed_asin(asin):
    search = driver.find_element(By.ID, "twotabsearchtextbox")
    search.send_keys(asin)
    search.send_keys(Keys.RETURN)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    regex = r'(\d+ result for)'
    if re.search(regex, soup.text):
        
        if int(remove_non_numeric(re.search(regex, soup.text).group())) == 0:
            return True
        else:
            return False
    else:
        return True

def no_of_pages(soup):
    feautures_div = soup.find("div", id = "detailBullets_feature_div")
    pages_num_regex = r'(\d+ pages)'
    if feautures_div:
        if re.search(pages_num_regex, feautures_div.text):
            return int(remove_non_numeric(re.search(pages_num_regex, feautures_div.text).group()))
        else:
            return None
    else:
        return None

def weight(soup):
    feautures_div = soup.find("div", id = "detailBullets_feature_div")
    weight_regex = r'(\d+ g)'
    if feautures_div:
        if re.search(weight_regex, feautures_div.text):
            return re.search(weight_regex, feautures_div.text).group().strip("g")
        else:
            return None
    else:
        return None

def dimensions(soup):
    feautures_div = soup.find("div", id = "detailBullets_feature_div")
    dimensions_regex = r'(\d+ x \d+ x \d+ cm)'
    if feautures_div:
        if re.search(dimensions_regex, feautures_div.text):
            return re.search(dimensions_regex, feautures_div.text).group()
        else:
            return None
    else:
        return None

current_status = "Active & Starred"

cursor.execute("SELECT asin FROM asin_status WHERE status = ?", (current_status,))
asins = cursor.fetchall()
for asin in asins:
    asin = asin[0]
    #create url from asin 
    url = "https://www.amazon.in/dp/" + "9355613458"
    driver.get(url)
    time.sleep(3)

    # driver.execute_script('return window.scrollTo(0, document.body.scrollHeight);')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    old_link = soup.find("span",class_="olp-new olp-link")
    if old_link:
        old_link = old_link.find("span").find("a")
        old_link = old_link.get("href")
        old_link = "https://www.amazon.in" + old_link
        driver.get(old_link)
        time.sleep(7)
        driver.execute_script('return window.scrollTo(0, document.body.scrollHeight);')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.ID, "all-offers-display-scroller")))
        time.sleep(5)

        div_element = driver.find_element(By.ID, "all-offers-display-scroller")
        driver.execute_script("arguments[0].scrollTop = 7000", div_element)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

    date = datetime.now().strftime("%d/%m/%Y")
    amzn_title = find_title(soup)
    best_seller_rank = regex_best_seller_rank(soup)
    ratings = rating(soup)
    star = stars(soup)
    seller_count = seller_nos(soup)
    main_seller = buy_box_seller(soup)
    main_seller_price = list_price(soup)
    main_seller_discount = list_discount(soup)
    review_count = written_reviews(asin)
    is_asin_suppressed = suppressed_asin(asin)
    category_rank = sub_category_rank(soup)
    sellers = sellers_list(soup)

    sub_rank_string = ""
    for sub_rank in category_rank:
        sub_rank_string = sub_rank_string + sub_rank[1] + " - " + sub_rank[2] + "\n"


    print(date, asin, amzn_title, best_seller_rank, category_rank, ratings, star, main_seller, main_seller_price, main_seller_discount, review_count, seller_count, sellers)

    #master data 
    master_data = {
        "date": date,
        "asin": asin,
        "best_seller_rank": best_seller_rank,
        "category_rank": sub_rank_string,
        "ratings": ratings,
        "star": star,
        "seller_count": seller_count,
        "amzn_title": amzn_title,
        "is_asin_suppressed": is_asin_suppressed,
        "main_seller": main_seller,
        "main_seller_price": main_seller_price,
        "main_seller_discount": main_seller_discount,
        "review_count": review_count
    }

    #insert data in master
    master_sheet.append_row(list(master_data.values()))

    #category rank data
    for sub_rank in category_rank:
        category_data = {
            "date": date,
            "asin": asin,
            "node": sub_rank[0],
            "category": sub_rank[1],
            "category_rank": sub_rank[2]
        }
        #insert data in category rank
        category_rank_sheet.append_row(list(category_data.values()))

    #seller data
    for seller in sellers:
        seller_data = {
            "date": date,
            "asin": asin,
            "seller_id": seller[0],
            "seller_name": seller[1],
            "seller_rating": seller[2],
            "seller_link": seller[3],
            "seller_price": seller[4],
        }
        #insert data in seller
        amzn_sellers_sheet.append_row(list(seller_data.values()))


    # #insert data in master
    # cursor.execute("INSERT INTO master (date, asin, best_seller_rank, category_rank, ratings, star, seller_count, amzn_title, is_asin_suppressed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE date = VALUES(date), best_seller_rank = VALUES(best_seller_rank), category_rank = VALUES(category_rank), ratings= VALUES(ratings), star = VALUES(star), seller_count = VALUES(seller_count), amzn_title = VALUES(amzn_title), is_asin_suppressed = VALUES(is_asin_suppressed)", (date, asin, best_seller_rank, sub_rank_string, ratings, star, seller_count, amzn_title, is_asin_suppressed))

    # #insert data in sub_category
    # for sub_rank in category_rank:
    #     cursor.execute("INSERT INTO sub_ranking (date, asin, category_name, node,sub_rank) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE date = VALUES(date), asin = VALUES(asin), category_name = VALUES(category_name), node = VALUES(node), sub_rank = VALUES(sub_rank)", (date, asin, sub_rank[1], sub_rank[0], sub_rank[2]))

    # #insert data in amzn_seller
    # for seller in sellers:
    #     print(seller)
    #     print(type(seller[1]))
    #     print(seller[1])
    #     cursor.execute("INSERT INTO amzn_sellers (date, asin, seller_id, seller_name, seller_link, rating) VALUES (%s, %s, %s, %s, %s,%s) ON DUPLICATE KEY UPDATE date = VALUES(date), asin = VALUES(asin), seller_id = VALUES(seller_id), seller_name = VALUES(seller_name), seller_link = VALUES(seller_link), rating = VALUES(rating)", (date, asin, seller[0], seller[1], seller[3], seller[2]))

    # connect.commit()
cursor.close()
connect.close()

