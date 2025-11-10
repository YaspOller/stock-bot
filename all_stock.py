import aiohttp
import asyncio
from bs4 import BeautifulSoup

PRODUCTS = [
    {
        "name": "Poke-Shop",
        "url": "https://www.poke-shop.dk/products/pokemon-tyranitar-ex-premium-collection?pr_prod_strat=e5_desc&pr_rec_id=e98ec1b67&pr_rec_pid=14839749181766&pr_ref_pid=15202939568454&pr_seq=uniform",
        "css_selector": "button.product-form__submit",
    },
    {
        "name": "MaxGaming",
        "url": "https://www.maxgaming.dk/dk/pokemon/jolteon-vmax-gift-box",
        "css_selector": "button, a",  # bredt — tjekker alle knapper og links
    },
]

WEBHOOK_URL = "https://discord.com/api/webhooks/1437232833906344010/jzgbDoY52k95VCgpL5j_cUPF-ZX0HuhjJ7SKHa6uEJEjDcFzoDc7zfrU9t6JOy2aq4u1"
USER_ID = "286567812510777345"
USER_AGENT = "Mozilla/5.0 (compatible; StockChecker/1.0)"

async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector, site_name):
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)

    for el in elements:
        text = el.get_text(strip=True).lower()

        # MaxGaming-specifikt tjek
        if site_name == "MaxGaming":
            if "tilføj" in text or "lægg" in text:
                return True

        # Poke-Shop
        if site_name == "Poke-Shop":
            if "kurv" in text and "udsolgt" not in text:
                return True

    return False

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

async def check_product(site):
    html = await fetch_html(site["url"])
    if is_in_stock(html, site["css_selector"], site["name"]):
        msg = f"**{site['name']}** har produktet på lager! 🔥\n{site['url']}"
        print(msg)
        await send_webhook(msg)
    else:
        print(f"{site['name']}: Produkt ikke på lager.")

async def main():
    await asyncio.gather(*(check_product(site) for site in PRODUCTS))

if __name__ == "__main__":
    asyncio.run(main())
