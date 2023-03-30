import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
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
from dateutil.relativedelta import *
import subprocess
from discord_webhook import DiscordWebhook, DiscordEmbed

subprocess.run(["python", "competetor_metrics.py"])


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
write_credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials/amazon-competetor.json', scope)
write_client = gspread.authorize(write_credentials)

competetor_sheet = write_client.open("Amazon").worksheet("Competetor")
competetor_asin = write_client.open("Amazon").worksheet("1 Nov Competetor")

# keep todays date as today's date but time as 00:00:00
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
three_month_old_date_From_today = today - relativedelta(months=3)
print(three_month_old_date_From_today)

competetors = {
    "Arihant Experts": "https://www.amazon.in/kindle-dbs/entity/author/B081S5Z7LG?_encoding=UTF8&node=976389031&offset=0&pageSize=1800&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "RPH Editorial Board": "https://www.amazon.in/kindle-dbs/entity/author/B07FCZRH8B?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Drishti Publication": "https://www.amazon.in/kindle-dbs/entity/author/B081S74ZWY?_encoding=UTF8&node=976389031&offset=0&pageSize=1700&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Disha Experts": "https://www.amazon.in/kindle-dbs/entity/author/B077SCV525?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Kiran Prakashan": "https://www.amazon.in/kindle-dbs/entity/author/B074Z91M7G?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Team Prabhat": "https://www.amazon.in/kindle-dbs/entity/author/B081CLXDYW?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Xamidea Editorial Board":  "https://www.amazon.in/kindle-dbs/entity/author/B08J45K8WR?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Books By Oswal - Gurukul": "https://www.amazon.in/kindle-dbs/entity/author/B09JZHKW8K?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Oswaal Editorial Board":  "https://www.amazon.in/kindle-dbs/entity/author/B07LB1G6YD?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "MTG Editorial Board": "https://www.amazon.in/kindle-dbs/entity/author/B081CTWW1L?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader",

    "Adda247 Publications":  "https://www.amazon.in/kindle-dbs/entity/author/B0844G8HJM?_encoding=UTF8&node=976389031&offset=0&pageSize=2000&searchAlias=stripbooks&sort=author-sidecar-rank&page=1&langFilter=default#formatSelectorHeader"
}


for key in competetors.keys():
    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)
    try: 
        driver.get(competetors[key])
        time.sleep(20)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        div1 = soup.find('div', id="searchWidget").find_all(
            'div', {"class": "a-fixed-left-grid-col a-col-right"})

        data = []
        gapi = 0
        url_count = 0
        for i in div1:

            if url_count < 3:

                crawl_date = datetime.now().strftime("%d-%m-%Y")
                title = i.find('div').find('div').find('div').find('a').text.strip()
                launch_date = i.find('div').find('div').find('div').find_all('span')[1].text.strip()
                launch_date = datetime.strptime(launch_date, '%d %b, %Y')
                launch_date_str = launch_date.strftime("%d-%m-%Y")
                href = i.find('div').find('div').find('div').find('a').get('href')
                link = urljoin("https://amazon.in", href)
                asin = link.split("/")[-2]
                competetor_name = key


                if launch_date < three_month_old_date_From_today:
                    url_count += 1
                    print("date wrong")
                    if url_count > 3:
                        break
                    continue
                else:
                    url_count = 0

                data = [launch_date_str, crawl_date, title, link, asin, competetor_name]
                # df = pd.DataFrame([data], columns=['Launch Date', 'Crawl Date', 'Title', 'Link', 'ASIN', 'Competetor Name'])
                # df.to_csv("competetor.csv", index=False, mode='a', header=False)

                print("data", data)
                print(gapi)
                competetor_asin.append_row(data)
                gapi += 1
                if gapi > 59:
                    time.sleep(60)
                    gapi = 0
            
        time.sleep(60)
        driver.close()
    except Exception as e:
        print("error", e)
        DiscordWebhook(url="https://discord.com/api/webhooks/1075110571193663589/F8R0zj0yhtsNVzcafVWTavpuIG2Q2DPQoKLG9JmiCZIscoomUVIm6sdGIk3hZlrXwd3b", content=f"competetor.py error {e}")
        continue

subprocess.run(["python", "competetor_metrics.py"])
