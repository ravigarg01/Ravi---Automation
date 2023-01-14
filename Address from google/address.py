from selenium import webdriver
from bs4 import BeautifulSoup
# create a new browser instance
driver = webdriver.Chrome()

# navigate to Google
driver.get("https://www.google.com")

# find the search box element and enter the query
soup = BeautifulSoup(driver.page_source, 'html.parser')
search_box = soup.find('input', attrs={'name': 'q'})
query = "1096-SARVODAY V M INT COLL PINAHAT AGRA"
search_box.send_keys(query)
search_box.submit()

# extract the address, phone number, and website from the search results
address = driver.find_element_by_css_selector(".LrzXr.zdqRlf.kno-fv")
phone = driver.find_element_by_css_selector(".LrzXr.zdqRlf.kno-fv > span:nth-child(2)")
website = driver.find_element_by_css_selector(".LrzXr.zdqRlf.kno-fv > span:nth-child(3)")

# print the extracted information
print("Address: ", address.text)
print("Phone: ", phone.text)
print("Website: ", website.text)

# close the browser
driver.quit()
