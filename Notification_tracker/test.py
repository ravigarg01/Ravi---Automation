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

links = asyncio.run(scrape('https://agnipathvayu.cdac.in/AV/'))

print(links)