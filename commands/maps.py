import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, search_osu_user, insert_user, delete_user
from console import print_to_console

class Maps(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    @app_commands.command(name="map_list", description="todo")
    async def map_list():
        return
        
async def setup(bot):
    await bot.add_cog(Maps(bot))