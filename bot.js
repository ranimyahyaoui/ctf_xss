const puppeteer = require('puppeteer');

// Configuration from environment or defaults
const APP_URL = process.env.APP_URL || 'http://172.16.238.10:3000'; 
const ADMIN_COOKIE_VAL = "ADMIN_SECRET_KEY_2026";
const CHROME_PATH = process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium';

/**
 * Utility to pause execution
 * @param {number} ms - Milliseconds to wait
 */
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function visit() {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: "new",
            executablePath: CHROME_PATH,
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage', 
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        const urlObj = new URL(APP_URL);
        const targetDomain = urlObj.hostname;

        console.log(`[${new Date().toLocaleTimeString()}] Preparing to visit: ${APP_URL}`);

        // Define the admin session cookie
        const cookies = [
            {
                name: 'session_id',
                value: ADMIN_COOKIE_VAL,
                domain: targetDomain,
                path: '/',
                httpOnly: false, 
                secure: false,  // Set to true if using HTTPS
                sameSite: 'Lax'
            }
        ];

        // 1. Set the cookies
        await page.setCookie(...cookies);

        // 2. Optional: Small delay to ensure the browser context is ready
        await delay(1000);

        // 3. Navigate to the target URL
        await page.goto(APP_URL, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });

        console.log(`[SUCCESS] Bot landed on: ${page.url()}`);

        // 4. Wait for XSS payloads or page interactions to execute
        await delay(5000);

    } catch (err) {
        console.error(`[ERROR] Bot encountered a problem: ${err.message}`);
    } finally {
        if (browser) {
            await browser.close();
            console.log(`[DEBUG] Browser closed. Next run in 30s.`);
        }
    }
}

// Start the loop
setInterval(visit, 30000);
visit();