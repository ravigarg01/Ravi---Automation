import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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

connect = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
'Server=Ravi-Digital-PC\SQLEXPRESS;'
'Database=amazon;''Trusted_Connection=yes;')
cursor = connect.cursor()

sheetname = "Amazon Ranks"
sheet = gc.open("products").worksheet(sheetname)
range = sheet.get("A2:F4")
priority_seller_sheet = gc.open('products').worksheet("priority seller")

mastersheet = gc.open('products').worksheet("Sheet51")
sellers_sheet = gc.open('products').worksheet("Sheet52")
all_priority_sellers_sheet = gc.open('products').worksheet("Sheet53")
subrank_sheet = gc.open('products').worksheet("Sheet54") 

options = webdriver.FirefoxOptions()
options.headless = False
driver = webdriver.Firefox(options=options)

def remove_non_numeric(s):
    return "".join(c for c in s if c.isnumeric())

def node_arr(node_str):
    numbers = re.findall(r'\b\d{10,}\b', node_str)
    array = list(map(int, numbers)) 
    return array

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
            seller_star = child_divs.find("i")
            if seller_star:
                seller_star = float(seller_star.get("class")[2].strip('a-star-mini-').replace('-', '.'))
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
    regex = r' #\d+ in(?![\w]) '
    regex1 = r' #\d+,\d+ in\b '
    regex2 = r' #\d+,\d+,\d+ in\b '
    regex3 = r' #\d+,\d+,\d+,\d+ in\b '

    sub_rank = []

    for expression in [regex, regex1, regex2, regex3]:
        sub_rank_match = re.finditer(expression, soup.text)
        if sub_rank_match:
            for match in sub_rank_match:
                print(match.group())
                text_node = soup.find(text=soup.text[match.start():match.end()])
                print(text_node)
                if text_node:
                    span_element = text_node.parent
                    a_tag = span_element.find("a").get("href")
                    node = re.search(r'\d+', a_tag).group()
                    category_name = span_element.find("a").text
                    rank = remove_non_numeric(match.group()[0:])
                    sub_rank.append([node, category_name, rank])
                else:
                    continue
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

#READ sheet for asin
for row in range:
    asin = row[0]
    status = row[1]
    book_code = row[2]
    company = row[3]
    book_name = row[4]
    price = row[5]
    cursor.execute("IF NOT EXISTS (SELECT * FROM asin_status WHERE asin = ?) BEGIN INSERT INTO asin_status (asin, status, book_code, company, book_name, price) VALUES (?, ?, ?, ?, ?, ?) END ELSE BEGIN UPDATE asin_status SET status = ?, book_code = ?, company = ?, book_name = ?, price = ? WHERE asin = ? END", (asin, asin, status, book_code, company, book_name, price, status, book_code, company, book_name, price, asin))
    connect.commit()

def sub_ranks_string (category_rank):
        sub_rank_string = ""
        for sub_rank in category_rank:
            sub_rank_string = sub_rank_string + sub_rank[1] + " - " + sub_rank[2] + "\n"
        return sub_rank_string

def get_adc_data():
    adc_data = requests.get('http://192.168.43.91:5000/asins').json()
    return adc_data

current_status = "Active & Starred"
for row in get_adc_data():
    asin = row['asin']
    status = row['status']
    if status == current_status:
        asin = row.get('asin')
        status = row['status']
        book_code = row['book_code']
        company = row['company']
        book_name = row['book_name']
        price = row['price']
        adc_nodes = node_arr(row['node'])

        #SQL: insert or update asin_status table
        cursor.execute("IF NOT EXISTS (SELECT * FROM asin_status WHERE asin = ?) BEGIN INSERT INTO asin_status (asin, status, book_code, company, book_name, price) VALUES (?, ?, ?, ?, ?, ?) END ELSE BEGIN UPDATE asin_status SET status = ?, book_code = ?, company = ?, book_name = ?, price = ? WHERE asin = ? END", (asin, asin, status, book_code, company, book_name, price, status, book_code, company, book_name, price, asin))
        connect.commit()

        #SQL: insert unique asin in All_time_best table
        cursor.execute("INSERT INTO All_time_best (asin) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM All_time_best WHERE asin = ?)", (asin, asin))
        connect.commit()
    else:
        continue

    url = "https://www.amazon.in/dp/" + asin
    print(url)
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
        time.sleep(4)
        driver.execute_script('return window.scrollTo(0, document.body.scrollHeight);')
        wait = WebDriverWait(driver, 10)

        time.sleep(5)

        # element = wait.until(EC.presence_of_element_located((By.ID, "all-offers-display-scroller")))
        try:
            div_element = driver.find_element(By.ID, "all-offers-display-scroller")
            driver.execute_script("arguments[0].scrollTop = 7000", div_element)
            time.sleep(3)

        except:
            print("No offers")
            div_element = None
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    
    date = datetime.now().strftime("%d/%m/%Y")
    amzn_title = find_title(soup)
    best_seller_rank = regex_best_seller_rank(soup)
    ratings = rating(soup)
    star = stars(soup)
    seller_count = seller_nos(soup)
    main_seller = buy_box_seller(soup)
    main_seller_mrp = list_price(soup)
    main_seller_discount = list_discount(soup)
    main_seller_price = selling_price(soup)
    review_count = written_reviews(asin)
    is_asin_suppressed = suppressed_asin(asin)
    category_rank = sub_category_rank(soup)
    sub_category_string = sub_ranks_string(category_rank)
    sellers = sellers_list(soup)

    #SQL: insert data into master table
    cursor.execute("INSERT INTO master (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_rank) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_category_string))
    connect.commit()

        #SQL: UPSERT master table
    #     cursor.execute('''MERGE INTO master AS target
    #     USING (SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) AS source (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_rank)
    #     ON (target.asin = source.asin) AND (target.date = source.date)
    #     WHEN MATCHED THEN
    #         UPDATE SET target.amzn_title = source.amzn_title, target.best_seller_rank = source.best_seller_rank, target.ratings = source.ratings, target.star = source.star, target.seller_count = source.seller_count, target.main_seller = source.main_seller, target.main_seller_mrp = source.main_seller_mrp, target.main_seller_discount = source.main_seller_discount, target.main_seller_price = source.main_seller_price, target.review_count = source.review_count, target.is_asin_suppressed = source.is_asin_suppressed, target.sub_rank = source.sub_rank
    #     WHEN NOT MATCHED THEN
    #         INSERT (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_rank) VALUES (source.date, source.asin, source.amzn_title, source.best_seller_rank, source.ratings, source.star, source.seller_count, source.main_seller, source.main_seller_mrp, source.main_seller_discount, source.main_seller_price, source.review_count, source.is_asin_suppressed, source.sub_rank);''')
    
    # # cursor.execute('''INSERT INTO master (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_rank)
    # VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # ON DUPLICATE KEY UPDATE amzn_title = VALUES(amzn_title), best_seller_rank = VALUES(best_seller_rank), ratings = VALUES(ratings), star = VALUES(star), seller_count = VALUES(seller_count), main_seller = VALUES(main_seller), main_seller_mrp = VALUES(main_seller_mrp), main_seller_discount = VALUES(main_seller_discount), main_seller_price = VALUES(main_seller_price), review_count = VALUES(review_count), is_asin_suppressed = VALUES(is_asin_suppressed), sub_rank = VALUES(sub_rank);
    # ''')
    

    # cursor.execute("""IF NOT EXISTS (SELECT * FROM master WHERE asin = @asin) 
    # BEGIN 
    # INSERT INTO master (date, asin, amzn_title, best_seller_rank, ratings, star, seller_count, main_seller, main_seller_mrp, main_seller_discount, main_seller_price, review_count, is_asin_suppressed, sub_rank)
    # VALUES (@date, @asin, @amzn_title, @best_seller_rank, @ratings, @star, @seller_count, @main_seller, @main_seller_mrp, @main_seller_discount, @main_seller_price, @review_count, @is_asin_suppressed, @sub_rank)
    # END 
    # ELSE 
    # BEGIN 
    # UPDATE master 
    # SET amzn_title = @amzn_title, 
    #     best_seller_rank = @best_seller_rank, 
    #     ratings = @ratings, 
    #     star = @star, 
    #     seller_count = @seller_count, 
    #     main_seller = @main_seller, 
    #     main_seller_mrp = @main_seller_mrp, 
    #     main_seller_discount = @main_seller_discount, 
    #     main_seller_price = @main_seller_price, 
    #     review_count = @review_count, 
    #     is_asin_suppressed = @is_asin_suppressed, 
    #     sub_rank = @sub_rank 
    # WHERE asin = @asin
    # END
    # """, {'asin': asin, 'date': date, 'amzn_title': amzn_title, 'best_seller_rank':     best_seller_rank, 'ratings': ratings, 'star': star, 'seller_count': seller_count, 'main_seller': main_seller, 'main_seller_mrp': main_seller_mrp, 'main_seller_discount': main_seller_discount, 'main_seller_price': main_seller_price, 'review_count': review_count, 'is_asin_suppressed': is_asin_suppressed, 'sub_rank': sub_rank})
    cursor.commit()

    # add data to seller sql table
    for seller in sellers:
        # try:
        #     cursor.execute("INSERT INTO All_sellers (date, asin, seller_name, merchant_id, rating_count, star, prime_status, seller_link, seller_price, buybox_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) date = VALUES(date), asin = VALUES(asin), seller_name = VALUES(seller_name), rating_count = VALUES(rating_count), star = VALUES(star), prime_status = VALUES(prime_status), seller_link = VALUES(seller_link), seller_price = VALUES(seller_price), buybox_status = VALUES(buybox_status)", (date, asin, seller[1], seller[0], seller[2], seller[3], seller[4], seller[5], seller[6], seller[7]))
        
        #     cursor.commit()
        # except:
        #     print("Error in seller table")
        #     pass

        #SQL: UPSERT sql query
        cursor.execute('''MERGE INTO All_sellers AS target
            USING (SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) AS source (date, asin, seller_name, merchant_id, rating_count, star, prime_status, seller_link, seller_price, buybox_status)
            ON (target.asin = source.asin) AND (target.date = source.date) AND (target.merchant_id = source.merchant_id)
            WHEN MATCHED THEN 
                UPDATE SET 
                    target.seller_name = source.seller_name, 
                    target.rating_count = source.rating_count, 
                    target.star = source.star, 
                    target.prime_status = source.prime_status, 
                    target.seller_link = source.seller_link, 
                    target.seller_price = source.seller_price, 
                    target.buybox_status = source.buybox_status
            WHEN NOT MATCHED THEN 
                INSERT (date, asin, seller_name, merchant_id, rating_count, star, prime_status, seller_link, seller_price, buybox_status) 
                    VALUES (source.date, source.asin, source.seller_name, source.merchant_id, source.rating_count, source.star, source.prime_status, source.seller_link, source.seller_price, source.buybox_status);
                    ''', (date, asin, seller[1], seller[0], seller[2], seller[3], seller[4], seller[5], seller[6], seller[7]))

        cursor.commit()


    # add data to sub category sql table
    for sub_category in category_rank:
        # cursor.execute("INSERT INTO sub_rank (date, asin, node, ranking, category_name) VALUES (?, ?, ?, ?, ?)", (date, asin, sub_category[0], sub_category[2], sub_category[1]))
        # cursor.commit()
        # cursor.execute("INSERT INTO sub_rank (date, asin, node, ranking, category_name) VALUES (?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE ranking = VALUES(ranking), category_name = VALUES(category_name)", (date, asin, sub_category[0], sub_category[2], sub_category[1]))
        # cursor.commit()

        # cursor.execute("IF NOT EXISTS (SELECT * FROM sub_rank WHERE date = ? AND asin = ? AND node = ?) BEGIN INSERT INTO sub_rank (date, asin, node, ranking, category_name) VALUES (?, ?, ?, ?, ?) END ELSE BEGIN UPDATE sub_rank SET ranking = ?, category_name = ? WHERE date = ? AND asin = ? AND node = ? END", (date, asin, sub_category[0], date, asin, sub_category[0], sub_category[2], sub_category[1], sub_category[2], sub_category[1], date, asin, sub_category[0]))

        #SQL: UPSERT sql query
        cursor.execute('''MERGE INTO sub_rank AS target
        USING (SELECT ?, ?, ?, ?, ?) AS source (date, asin, node, ranking, category_name)
        ON (target.date = source.date) AND (target.asin = source.asin) AND (target.node = source.node)
        WHEN MATCHED THEN
            UPDATE SET target.ranking = source.ranking, target.category_name = source.category_name
        WHEN NOT MATCHED THEN
            INSERT (date, asin, node, ranking, category_name) VALUES (source.date, source.asin, source.node, source.ranking, source.category_name);''', (date, asin, sub_category[0], sub_category[2], sub_category[1]))
        cursor.commit()

#SQL_UPDATE: All time best table 
atb_sql = '''
        UPDATE All_time_best
        SET atb_rank = master.best_seller_rank, atb_date = master.date
        FROM master 
        WHERE All_time_best.asin = master.asin
        AND All_time_best.atb_rank > master.best_seller_rank
        AND CAST(master.date AS DATE) = CAST(GETDATE() AS DATE);'''
cursor.execute(atb_sql)
cursor.commit()

#SQL_UPDATE: Columns in priority Sellers
row_count = 2
columns = []
priority_sellers = []
while priority_seller_sheet.row_count >= row_count:
    priority_seller = priority_seller_sheet.cell(row_count, 2).value
    row_count = row_count + 1
    column_name = priority_seller.replace(" ", "_")  # replace spaces with underscores
    if column_name not in columns:
        columns.append(f"{column_name} TINYINT")
        priority_sellers.append(priority_seller)

for column in columns:
    sql = f"IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'priority_sellers' AND COLUMN_NAME = '{column.split(' ')[0]}') ALTER TABLE priority_sellers ADD {column}"
    cursor.execute(sql)
cursor.commit()

# Update priority sellers table with asins
# cursor.execute('''INSERT INTO priority_sellers (date, asin)
#                 SELECT GETDATE(), asin
#                 FROM asin_status
#                 WHERE status = 'Active & Starred'
#                 ''')
# cursor.commit()

# cursor.execute('''IF NOT EXISTS (SELECT * FROM priority_sellers WHERE asin = @asin AND [date] = GETDATE())
# BEGIN
#     INSERT INTO priority_sellers ([date], asin)
#     VALUES (GETDATE(), @asin)
# END
# ELSE
# BEGIN
#     UPDATE priority_sellers
#     SET [date] = GETDATE()
#     WHERE asin = @asin AND [date] = GETDATE()
# END''')

#SQL_UPDATE : Priority Sellers

asins = cursor.execute('''Select asin from asin_status''').fetchall()
query = '''IF NOT EXISTS (SELECT * FROM priority_sellers WHERE asin = ? AND [date] = CAST(GETDATE() AS DATE))
    BEGIN
        INSERT INTO priority_sellers ([date], asin)
        VALUES (CAST(GETDATE() AS DATE), ?)
    END
    ELSE
    BEGIN
        UPDATE priority_sellers
        SET date = CAST(GETDATE() AS DATE)
        WHERE asin = ? AND [date] = CAST(GETDATE() AS DATE)
    END'''
for asin in asins:
    cursor.execute(f"{query}", (str(asin[0]), str(asin[0]), str(asin[0])))
cursor.commit()




# cursor.execute("IF NOT EXISTS (SELECT * FROM priority_sellers WHERE asin = ? and date = GETDATE()) BEGIN INSERT INTO priority_sellers (date, asin) VALUES (GETDATE(), ?) END ELSE BEGIN UPDATE priority_sellers SET date = GETDATE() WHERE asin = ? and date = GETDATE() END", (asin, asin, asin))
# cursor.commit()

# Fetch all asins to be updated
# asins_to_update = cursor.execute("SELECT asin FROM asin_status WHERE status = 'Active & Starred'").fetchall()
asins_to_update = cursor.execute("SELECT asin FROM priority_sellers WHERE date = CAST(GETDATE() AS DATE)").fetchall()
asins_to_update = [asin[0] for asin in asins_to_update]

# Update the priority sellers table with 0 or 1 for each priority seller
for asin in asins_to_update:
    # Get the sellers for this asin
    sellers = cursor.execute("SELECT merchant_id FROM all_sellers WHERE asin = ? AND [date] = CAST(GETDATE() AS DATE)", (asin,)).fetchall()
    sellers = [seller[0] for seller in sellers]

    # Build the SET clause of the update query
    set_clause = ''
    for priority_seller in priority_sellers:
        if priority_seller in sellers:
            set_clause += f"{priority_seller} = 1, "
        else:
            set_clause += f"{priority_seller} = 0, "
    set_clause = set_clause[:-2]

    # Execute the update query
    cursor.execute(f"UPDATE priority_sellers SET date = GETDATE(), {set_clause} WHERE asin = '{asin}'")
    cursor.commit()

#Update previous category rank column in master
# cursor.execute('''UPDATE master
# SET prev_sub_rank = (
# SELECT sub_rank
# FROM master sub
# WHERE sub.asin = master.asin
# AND sub.date = (
# SELECT MAX(date)
# FROM master sub2
# WHERE sub2.date < master.date
# AND sub2.date = DATEADD(day, -1, master.date)
# AND sub2.asin = master.asin
# )
# )
# FROM master;''')

cursor.execute('''UPDATE master
SET prev_sub_rank = subq.prev_sub_rank
FROM (
  SELECT asin, sub_rank, LAG(sub_rank) OVER (PARTITION BY asin ORDER BY date) AS prev_sub_rank
  FROM master
) subq
WHERE master.asin = subq.asin
  AND master.date = CAST(GETDATE() AS DATE);
''')

cursor.commit()


#read from master sql table where date will be today's date and create data to be sent to google sheet
cursor.execute('''SELECT master.*, asin_status.*
FROM master
JOIN asin_status ON master.asin = asin_status.asin
WHERE master.date = CONVERT(DATE, CONVERT(DATETIME, master.date, 102), 111)
''')

data = cursor.fetchall()
master_data_list = []
for row in data:
    date_str = row[0].strftime("%Y-%m-%d")
    print(row)

    print(row[0])
    master_data ={
        'date': date_str,
        'asin': row[1],
        'status': row[18],
        'book_code': row[19],
        'company': row[20],
        'book_name': row[21],
        'price': row[22],
        'best_seller_rank': row[2],
        'sub_rank': row[3],
        'ratings': row[4],
        'star': row[5],
        'seller_count': row[6],
        'amzn_title': row[7],
        'is_asin_suppressed': row[8],
        'main_seller': row[9],
        'main_seller_price': row[10],
        'main_seller_discount': row[11],
        'review_count': row[12],
        'main_seller_mrp': row[13],
        'ATB_rank': row[14],
        'ATB_date': row[15],
        'prev_sub_rank': row[16],
    }
    master_data_list.append(list(master_data.values()))
    #add data to google sheet
mastersheet.append_rows(master_data_list)


cursor.execute('''SELECT All_sellers.*, asin_status.*
FROM All_sellers
JOIN asin_status ON All_sellers.asin = asin_status.asin
WHERE All_sellers.date = CONVERT(DATE, CONVERT(DATETIME, All_sellers.date, 102), 111)
''')
seller_data = cursor.fetchall()

seller_data_list = []
for row in seller_data:
    date_str = row[0].strftime("%Y-%m-%d")
    print(row)
    seller_data = {
        'date': date_str,
        'asin': row[8],
        'book_code': row[13],
        'company': row[14],
        'book_name': row[15],
        'price': row[16],
        'seller_name': row[1],
        'merchant_id': row[2],
        'rating_count': row[3],
        'star': row[4],
        'prime_status': row[5],
        'seller_link': row[6],
        'seller_price': row[9],
        'buybox_status': row[10],
        'status': row[12]
    }
    seller_data_list.append(list(seller_data.values()))
sellers_sheet.append_rows(seller_data_list)

# get priority sellers and append them to google sheet
cursor.execute('''SELECT * from priority_sellers Where date = CONVERT(DATE, CONVERT(DATETIME, date, 102), 111)''') 
priority_sellers = cursor.fetchall()

ps_data = []
for row in priority_sellers:
    date_str = row[0].strftime("%Y-%m-%d")
    print(row)
    priority_seller_data = {
        'date': date_str,
        'asin': row[1],
        'seller_1': row[2],
        'seller_2': row[3],
        'seller_3': row[4],
        'seller_4': row[5],
        'seller_5': row[6],
        'seller_6': row[7],
        'seller_7': row[8],
    }
    ps_data.append(list(priority_seller_data.values()))
all_priority_sellers_sheet.append_rows(ps_data)

#get subrank data and append to google sheet
cursor.execute('''SELECT * from sub_rank Where date = CONVERT(DATE, CONVERT(DATETIME, date, 102), 111)''')
subrank_data = cursor.fetchall()
print(subrank_data)
sub_rank_data = []
for row in subrank_data:
    date_str = str(row[0].strftime("%Y-%m-%d"))
    print(row)
    subrank_data = {
        'date': date,
        'asin': row[1],
        'node_id': row[2],
        'sub_rank': str(row[3]),
        'category_name': row[4],
    }
    subrank_sheet.append_row(list(subrank_data.values()))

