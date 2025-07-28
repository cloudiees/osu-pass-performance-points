import discord
from discord.ext import commands
from config import DISCORD_BOT_KEY
import osu_api
import database
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")


async def load():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(DISCORD_BOT_KEY)
        
asyncio.run(main())