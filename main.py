import discord
from discord.ext import commands
from config import DISCORD_BOT_KEY
from commands import link
import osu_api
import database

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

link.setup(bot)

bot.run(DISCORD_BOT_KEY)