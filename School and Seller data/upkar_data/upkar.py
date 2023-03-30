from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, ThreadPoolExecutor, Districts, scope, credentials, gc

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://www.upkar.in/locate-agent.php")

wait = WebDriverWait(driver, 10)

pd = pandas.DataFrame()

data = []

toggle_1 = driver.find_element(By.ID, 'city')
all_cities = toggle_1.find_elements(By.TAG_NAME, "option")
all_cities_array = []


for city in all_cities:
    all_cities_array.append(city.text)

print(all_cities_array)
j = 0

while j < len(all_cities_array):
    print(j)
    toggle_1 = driver.find_element(By.ID, 'city')
    select_city = Select(toggle_1)
    select_city.select_by_visible_text(all_cities_array[j])

    time.sleep(5)

    table = driver.find_element(By.ID, 'ctl00_MainContent_gvAgents')
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        print(row.text)
        data.append(row.text)
    
    j += 1

df = pandas.DataFrame(data)
df.to_csv('upkar.csv', mode='a', header=False, index=False)



