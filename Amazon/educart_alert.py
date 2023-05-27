import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from scraping_functions import AmazonScraper, Helper
import slack


# slack_bot_token = 'GATXUWWYDFFHN4SK64F6H3X6UVUCRGMR6BXJ4JAPT2MMG5QI5VRQLQNE'
# slack_channel_name = '#amazon-sellers-tracker'
# slack_client = WebClient(token=slack_bot_token)

SLACK_TOKEN="xoxb-289367130914-5214824005669-ldaVQykGJm2QVJeDRQ232JII"
client = slack.WebClient(token=SLACK_TOKEN)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/credentials.json', scope)
gc = gspread.authorize(credentials)


while True:
    try:
        main_asin_and_seller_sheet = gc.open('Amazon').worksheet('main_sellers_and_asin')

        asins = main_asin_and_seller_sheet.get('A2:B' + str(main_asin_and_seller_sheet.row_count))
        main_sellers = main_asin_and_seller_sheet.get('C2:C' + str(main_asin_and_seller_sheet.row_count))
        

        # main_sellers = set([main_sellers])
        main_sellers = set([x[0] for x in main_sellers])

        helper = Helper()
        options = Options()
        options.headless = False
        driver = webdriver.Firefox(options=options)

        for Asin in asins: 
            print(Asin)
            asin = Asin[0]
        
            title = Asin[1]
            
            
            url = "https://amazon.in/gp/offer-listing/" + asin + '/ref=tmm_pap_new_olp_0?ie=UTF8&condition=new'
            driver.get(url)

            time.sleep(3)

            driver.execute_script('return window.scrollTo(0, document.body.scrollHeight);')
            wait = WebDriverWait(driver, 5)

            attempts = 0
            while attempts < 5:
                try:
                    wait.until(EC.presence_of_element_located(
                        (By.ID, "all-offers-display-scroller")))
                    div_element = driver.find_element(
                        By.ID, "all-offers-display-scroller")
                    driver.execute_script(
                        "arguments[0].scrollTop = 7000", div_element)
                    break
                except:
                    attempts += 1
                    time.sleep(5)
                    driver.execute_script(
                        'return window.scrollTo(0, document.body.scrollHeight);')
                    print("Scrolling")
                    continue
            
            time.sleep(3)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            
            scraper = AmazonScraper(soup=soup, driver=driver, helper=helper)
            sellers = scraper.sellers_list()

            if sellers: 
                for seller in sellers:
                    seller_id = seller[0]
                    if seller_id not in main_sellers:
                        seller_name = seller[1]
                        seller_rating = seller[2]
                        seller_star = seller[3]
                        prime_status = seller[4]
                        seller_link = seller[5]
                        price = seller[6] if seller[6] else "Not Available"
                        asin = asin if asin else "Not Available"
                        buybox_status = seller[7]
                        seller_count = len(sellers)
                        asin_link = "https://amazon.in/dp/" + asin
                    
                        print(type(buybox_status))
                        # message = "New seller for: " + str(asin) + "\n" + "Seller Name: " + seller_name + "\n" + "Seller Rating: " + str(seller_rating) + "\n" + "Seller Star: " + str(seller_star) + "\n" + "Prime Status: " + str(prime_status) + "\n" + "Seller Link: " + seller_link + "\n" + "Price: " + str(price) + "\n" + "Buybox Status: " + str(buybox_status) + "\n" + "Seller Count: " + str(seller_count) + "\n" + "ASIN Link: " + asin_link
                        # slack_client.chat_postMessage(channel=slack_channel_name, text=message)

                        if seller_link is not None:
                            if buybox_status == 1:
                                buybox_seller = "Yes"
                                message = (
                                    "Seller: <" + seller_link + "|" + seller_name + ">\n" +
                                    "ASIN: <" + asin_link + "|" + title + ">\n" +
                                    "Buybox Seller: " + buybox_seller + "\n"
                                )
                            if buybox_status == 0:
                                message = (
                                    "Seller: <" + seller_link + "|" + seller_name + ">\n" +
                                    "ASIN: <" + asin_link + "|" + title + ">\n"
                                )
                            
                            client.chat_postMessage(channel='#amazon-sellers-tracker',text=message)
                    else:
                        print("Seller already exists")
        time.sleep(3600)   

    except Exception as e:
        print(e)
        continue


