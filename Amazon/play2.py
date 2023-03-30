import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Define your credentials and open the sheet
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('amazon-credentials.json', scope)
gc = gspread.authorize(credentials)

write_credentials = ServiceAccountCredentials.from_json_keyfile_name('D:\Ravi_projects\Scraping\credentials\credentials.json', scope)
write_client = gspread.authorize(write_credentials)

examcart_sheet = write_client.open('Amazon').worksheet("1 Nov Competetor")

today = datetime.date.today().strftime("%d-%m-%Y")
print(today)

examcart_row_count = examcart_sheet.row_count
examcart_start_row = examcart_sheet.find(today, in_column=2)



# print(examcart_row_count)
# print(examcart_start_row.row)