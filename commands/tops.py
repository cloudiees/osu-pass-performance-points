# TODO: Fetch all users sorted by greatest o!ppp
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import get_leaderboard, get_top, search_disc_user, search_osu_user

class PageView(discord.ui.View):
    def __init__(self, *, user_id: int, pages: list[discord.Embed]):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.pages = pages
        self.current = 0
        
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You're not allowed to use these buttons.", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = self.current - 1
        if self.current < 0:
            self.current = 0
        await interaction.edit_original_response(embed=self.pages[self.current], view=self)
        
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = self.current + 1
        if self.current > len(self.pages):
            self.current = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

class Tops(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="leaderboard", description="Displays leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        leaderboard_data = await asyncio.to_thread(get_leaderboard)
        pages: list[discord.Embed] = []

        for i in range(0, len(leaderboard_data), 10):
            chunk = leaderboard_data[i:i+10]
            lines = [f"{i + j + 1}. {entry[0]} - {entry[1]}" for j, entry in enumerate(chunk)]
            embed = discord.Embed(
                title="Leaderboard",
                description="\n".join(lines),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(leaderboard_data) - 1) // 10 + 1}")
            pages.append(embed)

        view = PageView(user_id=interaction.user.id, pages=pages)
        await interaction.response.send_message(embed=pages[0], view=view)
        
    @app_commands.command(name="top", description="Get top plays")
    @app_commands.describe(user="osu! username", sort_by_stars="Sort by stars instead of o!ppp", sort_reverse="Sort in reverse order")
    async def top(self, interaction: discord.Interaction, user: str = None, sort_by_stars: bool = False, sort_reverse: bool = False):
        user_osu_id = None
        if user is None:
            user_data = (await asyncio.to_thread(search_disc_user, interaction.user.id))
            if user_data is None:
                embed = discord.Embed(title="Not Yet Linked", description="Please link your account before looking at your top plays by using `/link <osu_username>`.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                return
            
            user_osu_id = user_data[1]
            
        else:
            try:
                osu_user_data = await osu_api.user(user)
            except Exception:
                embed = discord.Embed(title="Error", description="Something went wrong. Please make sure you entered the username in correctly.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                return
            
            user_data = (await asyncio.to_thread(search_osu_user, osu_user_data.id))
            if user_data:
                user_osu_id = user_data[1]
            else:
                embed = discord.Embed(title="User Not Linked", description="This user has not linked their account.", color=discord.Color.orange())
                await interaction.response.send_message(embed=embed)
                return
        
        top_data = await asyncio.to_thread(get_top, user_osu_id, sort_by_stars, sort_reverse)
        pages: list[discord.Embed] = []

        for i in range(0, len(top_data), 10):
            chunk = top_data[i:i+10]
            lines = [f"{i + j + 1}. {entry[0]} [{entry[1]}] +{entry[3]} {entry[2]} Stars - {entry[4]}o!ppp" for j, entry in enumerate(chunk)]
            embed = discord.Embed(
                title="Top",
                description="\n".join(lines),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(top_data) - 1) // 10 + 1}")
            pages.append(embed)

        view = PageView(user_id=interaction.user.id, pages=pages)
        await interaction.response.send_message(embed=pages[0], view=view)
        
async def setup(bot):
    await bot.add_cog(Tops(bot))