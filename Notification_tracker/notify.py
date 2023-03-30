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

# Use your own credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet and get the URLs from the first sheet
sheet = client.open("Notification Tracker").worksheet("Links")
notfication_sheet = client.open("Notification Tracker").worksheet("Raw")

print(sheet.row_count)

india_time = datetime.now(pytz.timezone('Asia/Kolkata'))

prev_urls_file = 'prev_urls.txt'
if os.path.exists(prev_urls_file):
    with open(prev_urls_file) as f:
        prev_urls = set(json.load(f))
else:
    prev_urls = set()

google_api_count = 0

#Running the script for first time count
count = 0

while True:
    current_row = 2
    row_count = sheet.row_count
    while current_row <= row_count:
        boolean_value = sheet.cell(current_row,2).value
        print(f"Checking row: {current_row}")
        if boolean_value:
            url = sheet.cell(current_row,1).value
        if url is None:
            print("No URL found")
            continue
        if not url:
            print("No URL found")
            continue
        time.sleep(30)
        session = HTMLSession()
        try:
            r = session.get(url)
            soup = BeautifulSoup(r.html.html, 'html.parser')
            links = soup.find_all("a")
            for link in links:
                link_url = urljoin(url, link.get('href'))
                link_text = link.text
                if link_url not in prev_urls:
                    print(f"New URL found: {link_url} with text: {link_text}")
                    prev_urls.add(link_url)
                    data = {
                        "date": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y %H:%M:%S"),
                        "url": url,
                        "new_url": link_url,
                        "text": link_text,
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
            print("Error Occured while accessing: ",url)
            traceback.print_exc()
            data = {
                "date": time.strftime("%d/%m/%Y"),
                "url": url,
                "new_url": "Error Occured",
                "text": "Error Occured",
            }
            notfication_sheet.append_row(list(data.values()))
            google_api_count += 1
            if google_api_count >= 59: 
                print("Google API limit reached")
                time.sleep(60)
                google_api_count = 0
        finally:
            with open(prev_urls_file, 'w') as f:
                json.dump(list(prev_urls), f)
            current_row += 1
