const puppeteer = require('puppeteer');

function error () {
  console.log("no address found")
  return "no address found"
}

async function scrapegoogle() {
  const browser = await puppeteer.launch({headless: false});
  const page = await browser.newPage();
  await page.goto("https://www.google.com");

  const searchbox = await page.$('input[name = "q"]');
  const query= "1104-INDERBHAN GIRLS INTER COLLEGE AGRA";
  await searchbox.type(query);

  await searchbox.press("Enter");

  await page.waitForNavigation();

  try {let address = await page.$eval('.LrzXr', element => element.textContent)
  } catch (error) {const address = "no address found"}

  console.log("Address: ", address);

  await browser.close();
}

scrapegoogle().catch();

