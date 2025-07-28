# TODO: Delete all scores from user, then search through all scores from user and add o!ppp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, search_osu_user, insert_user

class Reload(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="reload", description="todo")
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.send_message("yuh2")
        
async def setup(bot):
    await bot.add_cog(Reload(bot))