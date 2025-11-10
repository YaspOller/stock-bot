import aiohttp
import asyncio
from bs4 import BeautifulSoup

# ---------------------------------
# PRODUKTER
# ---------------------------------
PRODUCTS = [
    {
        "name": "Poke-Shop",
        "url": "https://www.poke-shop.dk/products/pokemon-tcg-mega-charizard-ultra-premium-collection",
        "css_selector": "button.product-form__submit",
    },
    {
        "name": "MaxGaming",
        "url": "https://www.maxgaming.dk/dk/pokemon/pokemon-mega-charizard-ex-ultra-premium-samling?srsltid=AfmBOopEFVqC5LulItCCoeEDTNQp_vfctd-wy3rn70__XnR0rgj_tQw2mB4",
        "css_selector": "button",
    },
    {
        "name": "MuggleAlley",
        "url": "https://www.mugglealley.dk/shop/239-pokemon-kort/1839-upc-mega-charizard-x-ex/?srsltid=AfmBOopcr3DWezrAjsTQOgKQrozKSL8OFSaocIifp3ZjmrHNukjBFcMr7-g",
        "css_selector": "",  # Vi bruger .button-primary
    },
]

WEBHOOK_URL = "https://discord.com/api/webhooks/1437232833906344010/jzgbDoY52k95VCgpL5j_cUPF-ZX0HuhjJ7SKHa6uEJEjDcFzoDc7zfrU9t6JOy2aq4u1"
USER_ID = "286567812510777345"
USER_AGENT = "Mozilla/5.0 (compatible; StockChecker/1.0)"

# ---------------------------------
# HJÆLPEFUNKTIONER
# ---------------------------------
async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector, site_name):
    soup = BeautifulSoup(html, "html.parser")

    # ---- POKE-SHOP ----
    if site_name == "Poke-Shop":
        element = soup.select_one(selector)
        if not element:
            return False
        t = element.get_text(strip=True).lower()
        if "kurv" in t and "udsolgt" not in t:
            return True
        return False

    # ---- MAXGAMING ----
    elif site_name == "MaxGaming":
        text = soup.get_text().lower()
        if "tilgængelighed" in text:
            if "0 tilbage" in text or "kommer snart" in text:
                return False
            if "på lager" in text or "tilbage på lager" in text:
                return True
        for el in soup.select(selector):
            t = el.get_text(strip=True).lower()
            if "læg i indkøbsvogn" in t or "tilføj til kurv" in t:
                return True
        return False

    # ---- MUGGLEALLEY ----
    elif site_name == "MuggleAlley":
        # Tjek om der findes en knap med class "button-primary"
        if soup.select_one("button.button-primary"):
            return True
        return False

    return False

async def send_webhook(message):
    async with aiohttp.ClientSession() as session:
        payload = {
            "content": f"<@{USER_ID}> {message}",
            "allowed_mentions": {"users": [int(USER_ID)]}
        }
        async with session.post(WEBHOOK_URL, json=payload) as resp:
            if resp.status in (200, 204):
                print("✅ Besked sendt til Discord!")
            else:
                text = await resp.text()
                print(f"❌ Fejl ved afsendelse: {resp.status} - {text}")

# ---------------------------------
# HOVEDFUNKTION
# ---------------------------------
async def check_product(site):
    try:
        html = await fetch_html(site["url"])
        if is_in_stock(html, site.get("css_selector", ""), site["name"]):
            msg = f"**{site['name']}** har produktet på lager! 🔥\n{site['url']}"
            print(msg)
            await send_webhook(msg)
        else:
            print(f"{site['name']}: Produkt ikke på lager.")
    except Exception as e:
        print(f"⚠️ Fejl ved check af {site['name']}: {e}")

async def main():
    await asyncio.gather(*(check_product(site) for site in PRODUCTS))

if __name__ == "__main__":
    asyncio.run(main())
