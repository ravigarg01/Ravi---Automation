import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
from bs4 import BeautifulSoup
import pandas
from urllib.parse import urljoin
import time
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

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/Amazon-credentials.json', scope)
write_client = gspread.authorize(creds)

def log_error(error_message):
    filename = "flipkart_error.log"
    try:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")
        with open(filename, "a") as f:
            f.write(error_message + "\n")
    except Exception as e:
        # Handle the exception here, for example, by printing the error message
        print("Error logging the error:", str(e))

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
driver = webdriver.Firefox(options=options)

def remove_non_numeric(s):
    return "".join(c for c in s if c.isnumeric())

driver.get("https://flipkart.com")
time.sleep(5)

#find the search bar and search for the product

def find_product(ISBN):
    search_bar = driver.find_element(By.XPATH, "//input[@name='q']")
    search_bar.send_keys(ISBN)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_url = soup.find("div" , {"data-id" : str(ISBN)})
    if product_url:
        product_url = product_url.find("a")["href"]
        product_url = urljoin("https://flipkart.com", product_url)
        return product_url

def get_product_details(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sellers_page = soup.find("li", {"class": "_38I6QT"}).find("a")["href"]
    sellers_page = urljoin("https://flipkart.com", sellers_page)
    return sellers_page

def get_sellers_details(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sellers = soup.find_all("div", {"class": "_3rJyvX"})
    sellers_list = []
    for seller in sellers:
        seller_name = seller.find("div", {"class": "_3LWZlK"}).text
        seller_price = seller.find("div", {"class": "_1vC4OE"}).text
        seller_price = remove_non_numeric(seller_price)
        seller_rating = seller.find("div", {"class": "hGSR34"})
        if seller_rating:
            seller_rating = seller_rating.text
        else:
            seller_rating = "NA"
        sellers_list.append([seller_name, seller_price, seller_rating])
    return sellers_list
