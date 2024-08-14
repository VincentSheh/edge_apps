function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

const delay = (ms) => new Promise(res => setTimeout(res, ms));

const puppeteer = require('puppeteer');
// import puppeteer from "puppeteer"
(async () => {
  while (true) {
    let browser;  
    try {
      let browser = await puppeteer.launch({
        headless: true,
        args: [
          // `--use-fake-device-for-media-stream`,
          // `--use-fake-ui-for-media-stream`,
          `--no-sandbox`,
          '--disable-setuid-sandbox',
        ],
      });
      const page = await browser.newPage();

      await page.goto(
        `http://embymedia.com/web/index.html?#!/videos?serverId=50823b7138cd4d4fbe40f4583a34b234&parentId=3&tab=videos`,

      );
      //Choose User Page
      await page.waitForSelector('button[data-action="custom"]');
      await page.click('button[data-action="custom"]');    
      await delay(getRandomInt(10000))

      //Sign in Page
      await page.waitForSelector('#embyinput1');
      await page.type('#embyinput1', 'wmnlab256');    
      await page.click('.emby-button.paperSubmit');
      await delay(getRandomInt(10000))

      // await page.goto(
      //   "http://localhost:8097/web/index.html?#!/videos?serverId=50823b7138cd4d4fbe40f4583a34b234&parentId=3"
      // );
      await page.waitForSelector('button[title="Movies"]', { visible: true });
      await page.click('button[title="Movies"]');    
      await delay(getRandomInt(10000))

      await page.waitForSelector('button[title="Big Buck Bunny"]', { visible: true });
      await page.click('button[title="Big Buck Bunny"]');
      await delay(getRandomInt(10000))


      try {
        // Try to click on the "Resume" button
        await page.waitForSelector('button[title="Resume"]', { visible: true, timeout: 5000 }); // Additionally wait for up to 5000ms for the selector
        await page.click('button[title="Resume"]');
      } catch (error) {
        console.log('Could not find or click the "Resume" button, trying "Play" button instead.', error);
      
        // If the above fails, then try clicking the "Play" button
        await page.waitForSelector('button[title="Play"]', { visible: true, timeout: 5000 }); // Additionally wait for up to 5000ms for the selector
        await page.click('button[title="Play"]');
        await delay(getRandomInt(60000))

      }


      
      // Won't disconnect it, since we want to see it happening
    } catch (err) {
      console.error(err);
    }finally {
      console.log("Browser Closed")
      if (browser) await browser.close();
    }
  }
})();