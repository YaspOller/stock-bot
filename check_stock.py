# check_stock.py
# Tjekker om Pokémon Mega Charizard Ultra Premium Collection er på lager
# via poke-shop.dk og sender besked til Discord, hvis knappen findes.

import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup

PRODUCT_URL = os.getenv("PRODUCT_URL")
CSS_SELECTOR = os.getenv("CSS_SELECTOR")
MATCH_TEXT = os.getenv("MATCH_TEXT", "").lower()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # kanal-id som string
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; StockChecker/1.0)")

if not (PRODUCT_URL and CSS_SELECTOR and DISCORD_TOKEN and CHANNEL_ID):
    print("Manglende miljøvariabler. Sæt PRODUCT_URL, CSS_SELECTOR, DISCORD_TOKEN og CHANNEL_ID.")
    raise SystemExit(1)

async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector, match_text):
    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector)
    if not element:
        # Knappen findes ikke → antages ikke på lager
        return False
    # Knappen findes → antages på lager

        await send_discord_message(DISCORD_TOKEN, CHANNEL_ID, msg)

if __name__ == "__main__":
    asyncio.run(main())
