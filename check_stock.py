import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import discord

# Miljøvariabler fra GitHub secrets
PRODUCT_URL = os.getenv("PRODUCT_URL")
CSS_SELECTOR = os.getenv("CSS_SELECTOR")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Channel ID skal være integer
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; StockChecker/1.0)")

if not (PRODUCT_URL and CSS_SELECTOR and DISCORD_TOKEN and CHANNEL_ID):
    print("Manglende miljøvariabler! Tjek at alle secrets er sat korrekt.")
    raise SystemExit(1)

# Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_html(url):
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

def is_in_stock(html, selector):
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.select_one(selector))

async def send_discord_message(token, channel_id, message):
    intents = discord.Intents.default()
    async with discord.Client(intents=intents) as bot:
        await bot.login(token)
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            print("Kunne ikke finde Discord-kanalen. Tjek CHANNEL_ID.")

async def main():
    html = await fetch_html(PRODUCT_URL)
    if is_in_stock(html, CSS_SELECTOR):
        msg = f"**Produkt på lager:** {PRODUCT_URL}"
        print(msg)
        await send_discord_message(DISCORD_TOKEN, CHANNEL_ID, msg)
    else:
        print("Produkt ikke på lager.")

if __name__ == "__main__":
    asyncio.run(main())
