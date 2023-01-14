from webscraping import webdriver, By, BeautifulSoup, pandas, time, WebDriverWait, EC, Select, gspread, ServiceAccountCredentials, Options, ThreadPoolExecutor, Districts, scope, credentials, gc
import openpyxl 

driver = webdriver.Chrome()

driver.get("https://www.prabhatbooks.com/dealers-network.htm")

data_list = []

time.sleep(2)

toggle_1 = driver.find_element(By.ID, 'state')
all_states = toggle_1.find_elements(By.TAG_NAME, "option")
all_states_array = []

for state in all_states:
    all_states_array.append(state.text)

print(all_states_array)

i = 0

while i < len(all_states_array):
    toggle_1 = driver.find_element(By.ID, 'state')
    select_state = Select(toggle_1)
    select_state.select_by_visible_text(all_states_array[i])

    time.sleep(2)

    toggle_2 = driver.find_element(By.ID, 'city')
    all_cities = toggle_2.find_elements(By.TAG_NAME, "option")
    all_cities_array = []

    for city in all_cities:
        all_cities_array.append(city.text)
    
    j = 0

    while j < len(all_cities_array):
        toggle_2 = driver.find_element(By.ID, 'city')
        select_city = Select(toggle_2)
        select_city.select_by_visible_text(all_cities_array[j])

        wait = WebDriverWait(driver, 10)

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # dealer_boxes = soup.find_all('div', {'class': 'dealer-box'})
        dealer_boxes = soup.find('div', {'class': 'dealrs-list-cont'})
        
        if dealer_boxes.parent['id'] != "NewDelhi":
            dealer_boxes = dealer_boxes.find_all('div', {'class': 'dealer-box'})
            print('yes')
           
        for dealer_box in dealer_boxes:
            name = dealer_box.find('p').find('strong').text
            address = dealer_box.find('p').find('span').text
            contact_number = dealer_box.find_all('p')[1].text
            format_contact_number = contact_number.replace('Contact Number: ', '').replace('\t', '').replace('\n', '')
            data = {
                'state': all_states_array[i],
                'city': all_cities_array[j],
                'name': name,
                'address': address,
                'contact_number': format_contact_number
            }

            print(data)
            data_list.append(data)
        j += 1
    i += 1

df = pandas.DataFrame(data_list, columns=['state','city', 'name', 'address', 'contact_number'])
df.to_excel('Prabhat_new.xlsx', index=False)