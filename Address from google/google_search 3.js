const puppeteer = require("puppeteer");
const xlsx = require("xlsx");

async function scrapeGoogle(query) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto("https://www.google.com");

  const searchbox = await page.$('input[name = "q"]');
  await searchbox.type(query);

  await searchbox.press("Enter");

  await page.waitForNavigation();

  const address = await page
    .$eval(".LrzXr", (element) => element.textContent)
    .catch(error);

  await browser.close();
  return address;
}

function error() {
  return "no address found";
}

async function updateSheet() {
  const workbook = xlsx.readFile("products.xlsx");
  const sheets = workbook.SheetNames;

  let sheet = workbook.Sheets[sheets[3]];

  const range = xlsx.utils.decode_range(sheet["!ref"]);
  for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
    let row = xlsx.utils.encode_row(rowNum);
    let columnB = sheet[`A${row}`].v;
    let query = columnB;
    console.log(query);

    let address = await scrapeGoogle(query); // use the await keyword here
    console.log(address);

    let column8 = xlsx.utils.encode_col(10);
    let cellRef = `${column8}${row}`;
    sheet[cellRef] = { v: address, t: "s" };
    xlsx.writeFile(workbook, "products.xlsx");
  }
}

try {
  scrapeGoogle(query);
} catch (err) {
  console.log(err);
}
updateSheet(); // call the async function
