const puppeteer = require('puppeteer');

// Array of locations
const places = ["Taipei 101", "Tamsui", "Ximen", "Taipei Main Station"];

function getRandomPlace(placesArray) {
  const randomIndex = Math.floor(Math.random() * placesArray.length);
  return placesArray[randomIndex];
}

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

const delay = (ms) => new Promise(res => setTimeout(res, ms));

(async () => {
  while (true) {
    let browser;
    try {
      browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
      });
      const page = await browser.newPage();
      await page.goto('http://parkingtracker.com/map');
      console.log("Opened New browser");

      for (let i = 0; i < getRandomInt(25); i++) {
        const searchSelector = '.pac-target-input';
        const place = getRandomPlace(places);
        console.log("Finding Route to : ", place);
        await page.waitForSelector(searchSelector, { timeout: 5000 });
        await page.click(searchSelector, { clickCount: 3 }); // Selects existing text
        await page.type(searchSelector, place);

        const goButtonSelector = 'button.px-2.text-white.bg-black.border-l.rounded';
        await page.waitForSelector(goButtonSelector, { timeout: 5000 });
        await page.click(goButtonSelector);
        await delay(getRandomInt(10000));
      }

    } catch (err) {
      console.error(err);
    } finally {
      if (browser) await browser.close();
    }
  }
})();