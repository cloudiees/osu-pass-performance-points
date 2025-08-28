from config import DISCORD_BOT_KEY
import osu_api
import database
import os
import asyncio
import time
from auto_scan import scan_recent
from bot import bot
import discord


@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.playing, name="/help for help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")
    if not hasattr(bot, 'task_started'):
        asyncio.create_task(scan_recent())
        bot.task_started = True

async def load():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(DISCORD_BOT_KEY)
        
asyncio.run(main())