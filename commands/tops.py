# TODO: Fetch all users sorted by greatest o!ppp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import get_leaderboard, get_top, search_disc_user, search_osu_user

class Tops(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="leaderboard", description="todo")
    async def leaderboard(self, interaction: discord.Interaction):
        leaderboard_data = await asyncio.to_thread(get_leaderboard)
        leaderboard_str = ""
        for i in range(len(leaderboard_data)):
            leaderboard_str += f"{i + 1}. {leaderboard_data[i][0]} - {leaderboard_data[i][1]}\n"
            
        await interaction.response.send_message(leaderboard_str)
        
    @app_commands.command(name="top", description="get top plays")
    async def top(self, interaction: discord.Interaction, user: str = None, sort_by_stars: bool = False, sort_reverse: bool = False):
        user_osu_id = None
        if user is None:
            user_data = (await asyncio.to_thread(search_disc_user, interaction.user.id))
            if user_data is None:
                await interaction.response.send_message("Please link your account before viewing your top plays!")
                return
            
            user_osu_id = user_data[1]
            
        else:
            try:
                osu_user_data = await osu_api.user(user)
            except Exception:
                await interaction.response.send_message("Something went wrong. Please make sure you entered the username in correctly.")
                return
            
            user_data = (await asyncio.to_thread(search_osu_user, osu_user_data.id))
            if user_data:
                user_osu_id = user_data[1]
            else:
                await interaction.response.send_message("This user has not linked their osu account.")
                return
        
        top_data = await asyncio.to_thread(get_top, user_osu_id, sort_by_stars, sort_reverse)
        top_str = ""
        print(top_data)
        for i in range(len(top_data)):
            top_str += f"{i + 1}. {top_data[i][0]} [{top_data[i][1]}] +{top_data[i][3]} {top_data[i][2]} Stars - {top_data[i][4]}pp\n"
    
        print(top_str)
        await interaction.response.send_message(top_str)
        
async def setup(bot):
    await bot.add_cog(Tops(bot))