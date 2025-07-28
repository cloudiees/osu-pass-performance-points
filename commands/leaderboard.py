# TODO: Fetch all users sorted by greatest o!ppp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import search_disc_user, search_osu_user, insert_user

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="leaderboard", description="todo")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.send_message("yuh")
        
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))