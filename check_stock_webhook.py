import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup

# Miljøvariabler / GitHub secrets
PRODUCT_URL = os.getenv("PRODUCT_URL")
CSS_SELECTOR = os.getenv("CSS_SELECTOR")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
USER_ID = os.getenv("DISCORD_USER_ID")  # Discord bruger-ID til mention
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; StockChecker/1.0)")

if not (PRODUCT_URL and CSS_SELECTOR and WEBHOOK_URL and USER_ID):
    print("Manglende miljøvariabler! Tjek at secrets er sat korrekt.")
    raise SystemExit(1)

async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector):
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.select_one(selector))

async def send_webhook(message):
    async with aiohttp.ClientSession() as session:
        payload = {
            "content": f"<@{USER_ID}> {message}",
            "allowed_mentions": {"users": [int(USER_ID)]}
        }
        async with session.post(WEBHOOK_URL, json=payload) as resp:
            if resp.status in (200, 204):
                print("Besked sendt til Discord med mention!")
            else:
                text = await resp.text()
                print(f"Fejl ved afsendelse: {resp.status} - {text}")

async def main():
    html = await fetch_html(PRODUCT_URL)
    if is_in_stock(html, CSS_SELECTOR):
        msg = f"**Produkt på lager:** {PRODUCT_URL}"
        print(msg)
        await send_webhook(msg)
    else:
        print("Produkt ikke på lager.")

if __name__ == "__main__":
    asyncio.run(main())
