import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
from urllib.parse import urljoin, urlparse

def get_all_links(url, soup):
    links = []
    for a in soup.find_all('a', href=True):
        link = urljoin(url, a['href'])
        if urlparse(link).netloc == urlparse(url).netloc:
            links.append(link)
    return links

def get_pdf_links(url, visited=None):
    if visited is None:
        visited = set()
    visited.add(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = get_all_links(url, soup)
    pdf_links = [a for a in links if a.endswith('.pdf')]
    print(f"Found {len(pdf_links)} PDF links")
    non_pdf_links = [a for a in links if a not in pdf_links and a not in visited]
    for link in non_pdf_links:
        pdf_links.extend(get_pdf_links(link, visited))
    return pdf_links

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    with io.BytesIO(response.content) as open_pdf_file:
        pdf = pdfplumber.open(open_pdf_file)
        info = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if 'Name' in row and 'Contact' in row and 'Designation' in row:  # Replace with actual headers
                        info.append(row)
        pdf.close()
    return info

def extract_info_from_website(url):
    pdf_links = get_pdf_links(url)
    for link in pdf_links:
        print(f"Processing PDF: {link}")
        info = extract_text_from_pdf(link)
        for row in info:
            print(row)

# Call the function with the website URL
extract_info_from_website('http://www.mlzsbaraut.in/index.html')
