from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, ThreadPoolExecutor, Districts, scope, credentials, gc

def script1():
   
   sheet_name = 'Sultanchand'
   sheet = gc.open("products").worksheet(sheet_name)

   driver = webdriver.Chrome()

   driver.get("https://www.sultanchandandsons.com/Distributor.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ContentPlaceHolder1_drpselectregion')
   all_regions = toggle_1.find_elements(By.TAG_NAME, "option")
   all_regions_array = []
   
   time.sleep(4)

   for region in all_regions:
      all_regions_array.append(region.text)

   print(len(all_regions_array))
   j = 0

   while j < len(all_regions_array):
      toggle_1 = driver.find_element(By.ID, 'ContentPlaceHolder1_drpselectregion')
      select_region = Select(toggle_1)
      select_region.select_by_visible_text(all_regions_array[j])

      time.sleep(5)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      boxes = soup.find_all('div', {'class': 'dist-box'})

      for box in boxes:
         name = box.find('p', {'class': 'distName'}).strong.span.text
         address = box.find('p', {'class': 'distAdd'}).span.text
         email = box.find('p', {'class': 'distMail'}).span.text
         number = box.find('p', {'class': 'distNo'}).span.text
         data = {
            'Region': all_regions_array[j],
            'Name': name,
            'Address': address,
            'Email': email,
            'Number': number,
         }
         print(data)
         df = pandas.DataFrame(data, index=[0])
         df.to_csv('sultan.csv', mode='a', header=False, index=False)


             
      j += 1


script1()