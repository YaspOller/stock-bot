import aiohttp
import asyncio
from bs4 import BeautifulSoup

# -------------------------------
# Hardcoded værdier – ingen secrets
# -------------------------------
PRODUCTS = [
    {
        "name": "Poke-Shop",
        "url": "https://www.poke-shop.dk/products/pokemon-tcg-mega-charizard-ultra-premium-collection",
        "css_selector": "button.product-form__submit",  # 'Tilføj til kurv'-knap
    },
    {
        "name": "MaxGaming",
        "url": "https://www.maxgaming.dk/dk/pokemon/pokemon-mega-charizard-ex-ultra-premium-samling?srsltid=AfmBOopEFVqC5LulItCCoeEDTNQp_vfctd-wy3rn70__XnR0rgj_tQw2mB4",
        "css_selector": "button.buy-button",  # Knappen på MaxGaming (kan justeres hvis forkert)
    },
]

WEBHOOK_URL = "https://discord.com/api/webhooks/1437232833906344010/jzgbDoY52k95VCgpL5j_cUPF-ZX0HuhjJ7SKHa6uEJEjDcFzoDc7zfrU9t6JOy2aq4u1"
USER_ID = "286567812510777345"
USER_AGENT = "Mozilla/5.0 (compatible; StockChecker/1.0)"

# --------------------------------
# Hjælpefunktioner
# --------------------------------
async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector):
    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector)
    if not element:
        return False

    # For ekstra robusthed – tjek om knappen IKKE er disabled
    if element.has_attr("disabled"):
        return False
    text = element.get_text(strip=True).lower()
    if "udsolgt" in text or "ikke på lager" in text:
        return False
    return True

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

# --------------------------------
# Hovedfunktion
# --------------------------------
async def check_product(site):
    html = await fetch_html(site["url"])
    if is_in_stock(html, site["css_selector"]):
        msg = f"**{site['name']}** har produktet på lager! 🔥\n{site['url']}"
        print(msg)
        await send_webhook(msg)
    else:
        print(f"{site['name']}: Produkt ikke på lager.")

async def main():
    tasks = [check_product(site) for site in PRODUCTS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
