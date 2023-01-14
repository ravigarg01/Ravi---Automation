from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, ThreadPoolExecutor, Districts, scope, credentials, gc

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)

def script1(driver):   
   sheet_name = Districts[0]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = int(sheet.acell('B1').value)
   print(number_of_filled_rows)

   driver = webdriver.Chrome()

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   time.sleep(2)
   
   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []
   time.sleep(1)

   for school in all_schools:
      all_schools_array.append(school.text)

   print(len(all_schools_array))
   j = number_of_filled_rows

   while j < len(all_schools_array):
      print(j)
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(3)

      print(sheet_name)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': Districts[0],
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }
      print(data)
      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])      
      j += 1

def script2(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc


   sheet_name = Districts[1]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = int(sheet.acell('B1').value)

   driver = webdriver.Chrome()

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)
   
   time.sleep(2)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script3(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[2]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = int(sheet.acell('B1').value)

   driver = webdriver.Chrome()

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   time.sleep(2)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script4(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[3]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = int(sheet.acell('B1').value)

   driver = webdriver.Chrome()

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)
   time.sleep(2)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script5(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[4]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script6(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[5]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script7(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[6]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script8(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[7]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script9(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[8]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

def script10(driver):
   from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, Districts, scope, credentials, gc

   sheet_name = Districts[9]
   sheet = gc.open("products").worksheet(sheet_name)
   number_of_filled_rows = sheet.acell('B1').value

   driver.get("https://upmsp.edu.in/DistrictSchoolAdditionalInformationDetails.aspx")
   driver.wait = WebDriverWait(driver, 5)

   toggle_1 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_DistrictName')
   select_district = Select(toggle_1)
   select_district.select_by_visible_text(sheet_name)

   toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
   all_schools = toggle_2.find_elements(By.TAG_NAME, 'option')
   all_schools_array = []

   for school in all_schools:
      all_schools_array.append(school.text)

   j = number_of_filled_rows

   while j < len(all_schools_array):
      toggle_2 = driver.find_element(By.ID, 'ctl00_cphBody_ddl_vc_SchoolName')
      select_school = Select(toggle_2)
      select_school.select_by_visible_text(all_schools_array[j])
      time.sleep(1)

      view_report_button = driver.find_element(By.ID, 'ctl00_cphBody_btnViewReport')
      view_report_button.click()
      time.sleep(3)

      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')

      school_code_name = soup.find('span', id='ctl00_cphBody_lbl_SchoolName').text
      udice_code = soup.find('span', id='ctl00_cphBody_txt_vc_UDiasCode').text
      pincode = soup.find('span', id='ctl00_cphBody_txt_vc_PinCode').text
      block = soup.find('span', id='ctl00_cphBody_lbl_vc_BlockName').text
      tehsil = soup.find('span', id='ctl00_cphBody_lbl_vc_TehsilName').text
      management_name = soup.find('span', id='ctl00_cphBody_txt_vc_DirectorName').text
      school_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation_Schl').text
      govt_latitude = soup.find('span', id='ctl00_cphBody_lbl_vc_GeoLocation').text
      school_type = soup.find('select', {'id': 'ctl00_cphBody_ddl_ch_SchoolStatus_HSorIN', 'class': 'vc_TextBox'}).find('option', {'selected': 'selected'}).text
      data = {
            'School Code Name': school_code_name,
            'UDICE Code': udice_code,
            'Management Name': management_name,
            'School Type': school_type,
            'Pincode': pincode,
            'District': sheet_name,
            'Block': block,
            'Tehsil': tehsil,
            'School Latitude': school_latitude,
            'Govt Latitude': govt_latitude,
      }

      df = pandas.DataFrame(data, index=[0])
      sheet.append_row(df.values.tolist()[0])
      j += 1

driver = webdriver.Chrome()

executor = ThreadPoolExecutor(max_workers=10)
futures = [executor.submit(script1, driver)]
#  executor.submit(script2, driver), executor.submit(script3, driver), 
#                   executor.submit(script4, driver), executor.submit(script5, driver), executor.submit(script6, driver), 
#                   executor.submit(script7, driver), executor.submit(script8, driver), executor.submit(script9, driver), 
#                   executor.submit(script10, driver)]

for future in futures:
   future.result()

# driver.quit()