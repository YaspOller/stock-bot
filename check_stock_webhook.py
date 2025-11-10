import aiohttp
import asyncio
from bs4 import BeautifulSoup

# -------------------------------
# Hardcoded værdier – ingen secrets
# -------------------------------
PRODUCT_URL = "https://www.poke-shop.dk/products/pokemon-tcg-mega-charizard-ultra-premium-collection"
CSS_SELECTOR = "button.product-form__submit"
WEBHOOK_URL = "https://discord.com/api/webhooks/1437232833906344010/jzgbDoY52k95VCgpL5j_cUPF-ZX0HuhjJ7SKHa6uEJEjDcFzoDc7zfrU9t6JOy2aq4u1"
USER_ID = "286567812510777345"  # Tal, fx 123456789012345678
USER_AGENT = "Mozilla/5.0 (compatible; StockChecker/1.0)"

# --------------------------------
# Script
# --------------------------------
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
