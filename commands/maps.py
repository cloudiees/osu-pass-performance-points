import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from osu_api import osu_api
from db_commands import get_all_maps
from console import print_to_console
from page_view import PageView

class Maps(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    @app_commands.command(name="map_list", description="todo")
    async def map_list(self, interaction: discord.Interaction):
        print_to_console(f"User {interaction.user.id}'s is attempting to access the map list")
        maps = get_all_maps()
        pages: list[discord.Embed] = []

        for i in range(0, len(maps), 10):
            chunk = maps[i:i+10]
            lines = [f"{i + j + 1}. **[{entry[7]} [{entry[8]}]](https://osu.ppy.sh/b/{entry[0]})**\n\u00A0\u00A0\u00A0\u00A0{entry[9]}⭐ - {round(entry[1], 2)}ppp" for j, entry in enumerate(chunk)]
            embed = discord.Embed(
                title=f"Map List",
                description="\n".join(lines),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {(i // 10) + 1} of {(len(maps) - 1) // 10 + 1}")
            pages.append(embed)
        if len(pages) == 0:
            embed = discord.Embed(title="No Maps", description="There are no maps to display", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
        else:
            view = PageView(user_id=interaction.user.id, pages=pages)
            await interaction.response.send_message(embed=pages[0], view=view)
        print_to_console(f"User {interaction.user.id}'s map list request was successful")
        return
        
async def setup(bot):
    await bot.add_cog(Maps(bot))