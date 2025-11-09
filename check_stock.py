# check_stock.py
# Kører ét tjek og sender besked til Discord kanal via bot-token.

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
    el = soup.select_one(selector)
    if not el:
        print("Selector matchede ingen elementer.")
        return False
    text = el.get_text(separator=" ").strip().lower()
    if match_text:
        return match_text in text
    negative = ["out of stock", "udsolgt", "ikke på lager", "sold out", "ikke tilgjengelig"]
    for k in negative:
        if k in text:
            return False
    return True

async def send_discord_message(token, channel_id, message):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    payload = {"content": message}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status in (200,201):
                print("Besked sendt til Discord.")
            else:
                text = await resp.text()
                print(f"Fejl ved afsendelse til Discord: {resp.status} - {text}")

async def main():
    html = await fetch_html(PRODUCT_URL)
    instock = is_in_stock(html, CSS_SELECTOR, MATCH_TEXT)
    print("In stock:", instock)
    if instock:
        msg = f"**Produkt på lager:**\n{PRODUCT_URL}"
        await send_discord_message(DISCORD_TOKEN, CHANNEL_ID, msg)

if __name__ == "__main__":
    asyncio.run(main())
