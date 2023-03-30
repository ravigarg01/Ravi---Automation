// const puppeteer = require('puppeteer');

// const {google} = require('googleapis');
// const credentials = require('./credentials5.json');
// const sheetId = 'GUBGMHVpwcTsPFvNNVdG5DKtpv6UwksAfzw5aULcGzgG';

// async function accessSpreadsheet() {
//   const client = await google.auth.fromJSON(credentials);
//   client.scopes = ['https://www.googleapis.com/auth/spreadsheets'];
//   await client.authorize();
//   const sheets = google.sheets({version: 'v4', client});
//   const sheet = await sheets.spreadsheets.get({spreadsheetId: sheetId});
//   console.log(sheet.data);
// }

// accessSpreadsheet();

// const GoogleSpreadsheet = require('google-spreadsheet');
// const { promisify } = require('util');
// const credentials = require('./credentials2.json');

// async function accessSpreadsheet () {
//   const workbook = new GoogleSpreadsheet('GUBGMHVpwcTsPFvNNVdG5DKtpv6UwksAfzw5aULcGzgG');
//   await promisify (workbook.useServiceAccountAuth)(credentials);
//   const info = await promisify (workbook.getInfo)();
//   const sheet = info.worksheets.find((sheet) => sheet.title === 'Script1 -Agra');
//   console.log(sheet);
// }

// const sheetId = 'GUBGMHVpwcTsPFvNNVdG5DKtpv6UwksAfzw5aULcGzgG';

// const scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'];
// const key = './credentials.json'

// const auth = new GoogleAuth({
//   key: key,
//   scopes: scope,
// })

// const client = auth.getClient()

// const gc = new gspread.GoogleSpreadsheet(sheetId)
//  gc.useServiceAccountAuth(client)

// gc.getInfo((err, info) => {

//   if (err) {
//     console.log(err)
//   } else {
//     const sheet = info.worksheets.find((sheet) => sheet.title === 'Script1 -Agra')
//   }

//   if (sheet) {
//     let lastRow = sheet.rowCount
//     let row = 2;
//     console.log(lastRow)

//     function error () {
//       console.log("no address found")
//       return "no address found"
//     }

//     while (row <= lastRow) {
//       let query = sheet.cell(row, 1).getValue()

//       async function scrapegoogle(query) {
//         const browser = await puppeteer.launch({headless: false});
//         const page = await browser.newPage();
//         await page.goto("https://www.google.com");

//         const searchbox = await page.$('input[name = "q"]');
//         await searchbox.type(query);

//         await searchbox.press("Enter");

//         await page.waitForNavigation();

//         const address = await page.$eval('.LrzXr', element => element.textContent).catch(error);

//         console.log("Address: ", address);

//         sheet.updateCell(row, 8, address)

//         await browser.close();
//       }

//       try{
//         scrapegoogle(query)
//       }catch(err){
//         console.log(err)
//       }
//       row++
//     }
//   }
// })

const puppeteer = require("puppeteer");
const xlsx = require("xlsx");

// const workbook = xlsx.readFile("products.xlsx");
// const sheets = workbook.SheetNames;

// for (let i = 0; i < sheets.length; i++) {
//   let sheet = workbook.Sheets[sheets[i]];

//   const range = xlsx.utils.decode_range(sheet["!ref"]);
//   for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
//     if(rowNum === range.e.r) break;
//     let row = xlsx.utils.encode_row(rowNum);
//     let columnB = sheet[`A${row}`].v;
//     let query = columnB;
//     console.log(query);

//     let address = scrapegoogle(query);

//     let column8 = xlsx.utils.encode_col(8);
//     let cellRef = `${column8}${row}`;
//     sheet[cellRef] = { v: address, t: "s" };
//     xlsx.writeFile(workbook, "products.xlsx");
//   }
// }
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

// const xlsx = require("xlsx");
const cheerio = require("cheerio");
const request = require("request");

// const workbook = xlsx.readFile("Book1.xlsx");
// const sheets = workbook.SheetNames;

// for (let i = 0; i < sheets.length; i++) {
//   let sheet = workbook.Sheets[sheets[i]];

//   const range = xlsx.utils.decode_range(sheet["!ref"]);
//   for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
//     if (rowNum === range.e.r) break;
//     let row = xlsx.utils.encode_row(rowNum);
//     let columnB = sheet[`B${row}`].v;
//     let query = columnB;
//     console.log(query);

//     let address = scrapegoogle(query);

//     let column8 = xlsx.utils.encode_col(8);
//     let cellRef = `${column8}${row}`;
//     sheet[cellRef] = { v: address, t: "s" };
//     xlsx.writeFile(workbook, "products.xlsx");
//   }
// }

// async function scrapeGoogle(query) {
//   request(
//     `https://www.google.com/search?q=${query}`,
//     (error, response, html) => {
//       if (!error && response.statusCode == 200) {
//         console.log('its woking')
//         const $ = cheerio.load(html);
//         const address = $(".LrzXr").text();
//         console.log(address);
//         return address;
//       } else {
//         console.log("No address found");
//         return "no address found";
//       }
//     }
//   );
// }

async function updateSheet() {
  const workbook = xlsx.readFile("products.xlsx");
  const sheets = workbook.SheetNames;

  let sheet = workbook.Sheets[sheets[1]];

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
