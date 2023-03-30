import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import time
from requests_html import HTMLSession
import os
import json
from urllib.parse import urljoin
import traceback
import pytz
from datetime import datetime
import sqlite3
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from pyppeteer import launch
import asyncio
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup
import time
from requests_html import HTMLSession
import os
import json
from urllib.parse import urljoin
import traceback
import pytz
from datetime import datetime
import sqlite3
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback

# asyncio.run(main())



# Use your own credentials to access the Google Sheet
scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
  'D:\Ravi_projects\Scraping\credentials\credentials_2_0.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet and get the URLs from the first sheet
sheet = client.open("Notification Tracker").worksheet("Links")
notfication_sheet = client.open("Notification Tracker").worksheet("Raw_2.0")

print(sheet.row_count)

india_time = datetime.now(pytz.timezone('Asia/Kolkata'))

conn = sqlite3.connect('prev_urls.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS prev_urls (url TEXT UNIQUE)''')

async def scrape(url):
  browser = await launch()
  page = await browser.newPage()
  await page.goto(url)

  # Get all the links on the page
  links = await page.evaluate("""() => {
    const anchors = Array.from(document.querySelectorAll('a'));
    return anchors.map(a => a.href);
  }""")
  await browser.close()
  return links

async def main(url):
    await scrape(url)


def url_exists(url):
  cursor.execute('''SELECT * FROM prev_urls WHERE url = ?''', (url, ))
  return cursor.fetchone() is not None


google_api_count = 0

#Running the script for first time count
count = 0
while True:
  try:
    while True:
      current_row = 2
      row_count = sheet.row_count
      print(row_count)
      while current_row <= row_count:
        while True:
          try:
            boolean_value = sheet.cell(current_row, 3).value
            break
          except Exception as e:
            print("Error: ", e)
            print("Retrying...")
            time.sleep(60)
            continue
        print(f"Checking row: {current_row}")
        url = None
        if boolean_value == 'TRUE':
          print(boolean_value)
          print(type(boolean_value))
          url = sheet.cell(current_row, 1).value
        if url is None:
          print("No URL found")
          current_row += 1
          continue
        if not url:
          print("No URL found")
          continue
        try:
          links = asyncio.run(scrape(url))
          for link in links:
            link_url = link
            link_text = link
            if not url_exists(link_url):
              print(f"New URL found: {link_url} with text: {link_text}")
              cursor.execute('''INSERT INTO prev_urls VALUES (?)''',
                             (link_url, ))
              conn.commit()
              data = {
                "time":
                datetime.now(
                  pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S"),
                "date":
                datetime.now(
                  pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y"),
                "url":
                url,
                "new_url":
                link_url,
                "text":
                link_text,
              }
              notfication_sheet.append_row(list(data.values()))
              # last_row = notfication_sheet.get_last_row() + 1
              # notfication_sheet.insert_rows(last_row, values=list(data.values()))
              google_api_count += 1

              if google_api_count >= 59:
                print("Google API limit reached")
                time.sleep(60)
                google_api_count = 0
        except Exception:
          print("Error Occured while accessing: ", url)
          traceback.print_exc()
          data = {
            "time":
            datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S"),
            "date":
            time.strftime("%d/%m/%Y"),
            "url":
            url,
            "new_url":
            "Error Occured",
            "text":
            "Error Occured",
          }
          notfication_sheet.append_row(list(data.values()))
          google_api_count += 1
          if google_api_count >= 59:
            print("Google API limit reached")
            time.sleep(60)
            google_api_count = 0
        finally:
          current_row += 1

  except Exception as e:
    tb_str = traceback.format_tb(e.__traceback__)[0]
    error = f"{e.__class__.__name__}: {e} on line {tb_str.split(',')[1].lstrip().split(' ')[1]}"
    DiscordWebhook(url="https://discord.com/api/webhooks/1075110571193663589/F8R0zj0yhtsNVzcafVWTavpuIG2Q2DPQoKLG9JmiCZIscoomUVIm6sdGIk3hZlrXwd3b", content=f"{error}").execute()
    print("Error: ", e)
    print("error occured in script")
    time.sleep(60)
    current_row += 1
    continue
