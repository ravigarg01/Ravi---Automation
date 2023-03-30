from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

def remove_non_numeric(s):
    return "".join(c for c in s if c.isnumeric())

# Set up the credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('D:\Ravi_projects\Scraping\credentials\credentials.json', scope)

# Connect to the Google Sheet
gc = gspread.authorize(credentials)
name = "EDUCART"
sheet = gc.open("products").worksheet(name)

# Set the range of cells to read the URLs from
url_range = "F2:F" + str(sheet.row_count)
print(url_range)

# Set the range of cells to write the best seller ranks to
rank_range = "H2:H" + str(sheet.row_count)

#Set the range of cells to write the no. of amazon reviews to
# review_range = "D2:D295"

#Set the range of cell to write the subranks
sub_rank_range = "E2:E295"

# Read the URLs from the specified range
urls = sheet.range(url_range)

#setup the proxy server 
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = ''

#Set up the options for Firefox browser
options = Options()

#Set the incognito mode flag
options.add_argument('--incognito')
options.add_argument('--headless')

# Set up the desired capabilities
capabilities = DesiredCapabilities.FIREFOX.copy()

# Set the user agent to a fake user agent
capabilities['acceptSslCerts'] = True
capabilities['acceptInsecureCerts'] = True
capabilities['acceptLanguage'] = 'en-US'
capabilities['userAgent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'

# Set up the webdriver
driver = webdriver.Firefox(capabilities=capabilities, options=options)

# Set up an array to hold the best seller ranks
ranks = []

#Set up an array to hold the reviews
# reviews = []

#Set up an array to hold the sub ranks
# sub_ranks = []
# Use a for loop to iterate over the URLs
for i, url in enumerate(urls):
  driver.get(url.value)
  # Execute JavaScript to generate the element containing the best seller rank
  driver.execute_script('return window.scrollTo(0, document.body.scrollHeight);')

  # Wait for the page to load
  time.sleep(10)

  # Get the page source
  html = driver.page_source

  # Use the BeautifulSoup library to parse the HTML
  soup = BeautifulSoup(html, 'html.parser')

  # Define the regular expression to extract the best seller rank
  rank_regex = r'#\d+,\d+ in Books \('
  rank_regex1 = r'#\d+ in Books \('
  rank_regex2 = r'#\d+,\d+,\d+ in Books \('

  rank_match = re.search(rank_regex, soup.text)
  if rank_match == None:
      rank_match = re.search(rank_regex1, soup.text)
      if rank_match == None:
         rank_match = re.search(rank_regex2,soup.text)

  if rank_match:
    # If the regular expression matched some text, extract the best seller rank
    best_seller_rank = rank_match.group()
    print(f'Best seller rank: {best_seller_rank}')
    s = best_seller_rank
    print(remove_non_numeric(s))
    p = remove_non_numeric(s)
    # sheet.update_cell(i+1, 3, p)
    ranks.append(p)
    sheet.update_cell(i+2, 8, p)
    
  else:
  # If the regular expression didn't match any text, print a message
    print('Could not find best seller rank')
    ranks.append("NA")
    sheet.update_cell(i+2, 8, "N/A")
    # sheet.update_cell(i+1, 3, "N/A")


  # customer_review = soup.find('span', {'id': 'acrCustomerReviewText'})
  # if customer_review: 
  #   totalreviews = "".join(customer_review.stripped_strings)
  #   print(totalreviews)
  #   reviews.append(totalreviews)
  # else:
  #   reviews.append("NA")

# ranks_as_rows = [[rank] for rank in ranks]
# reviews_as_rows = [[review] for review in reviews]
# sub_ranks_as_rows = [[subrank] for subrank in sub_ranks]
# sheet.update(rank_range, ranks_as_rows)
# sheet.update(review_range, reviews_as_rows)
# sheet.update(sub_ranks, sub_rank_range)
# sheet.update(sub_rank_range, sub_ranks_as_rows)

driver.close()
