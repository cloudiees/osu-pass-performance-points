import discord
from discord.ext import commands
from discord import app_commands
from console import print_to_console
from page_view import PageView

# Dict of commands and a simple description
commands_list = {
            "link" : "Links osu! profile to your discord",
            "unlink": "Unlink your osu! profile from your discord",
            "map_list": "Get the playable map list",
            "submit": "Submit a score using it's score id",
            "autosubmit": "Automatically scan and submit valid pass scores",
            "submit_recent": "Submit the most recent passed score",
            "map_leaderboard": "Displays a map's leaderboard",
            "leaderboard": "Displays ppp leaderboard",
            "top": "Displays top plays"
        }

# Dict of commands and a more detailed description
commands_list_detailed = {
            "link" : "Links osu! profile to your discord\n\nThe *user* field is where you enter your osu! username\n\nYou must link your account before you start submitting scores\n\nYou can only link to one account\n\nIf you accidently link to the wrong account you can use **/unlink** to unlink the osu! account from your discord account",
            "unlink": "Unlink your osu! profile from your discord\n\nYou must have your account linked before you can unlink",
            "map_list": "Get the playable map list\n\nThese are all the maps that you can play to get ppp",
            "submit": "Submit a score using it's score id\n\nThe *score_id* field is the id of the score you want to submit\n\nPlease note that currently only STABLE scores will be allowed\n\nThe current legal mod list is: HD, HR, SD/PF, DT/NC, FL, and SO\nAny mod not in this mod list will result in a score not being able to be submitted",
            "autosubmit": "Automatically scan and submit valid pass scores\n\nThis command has a cooldown of 1 hour\n\nThis command takes a bit so please be patient\n\nPlease note that currently only STABLE scores will be allowed\n\nThe current legal mod list is: HD, HR, SD/PF, DT/NC, FL, and SO\nAny mod not in this mod list will result in a score not being able to be submitted",
            "submit_recent": "Submit the most recent passed score\n\nDo note that once you are linked there is an automatic scanner that runs every so often to submit your scores for you, so sometimes when you submit a score it might've already been submitted\n\nPlease note that currently only STABLE scores will be allowed\n\nThe current legal mod list is: HD, HR, SD/PF, DT/NC, FL, and SO\nAny mod not in this mod list will result in a score not being able to be submitted",
            "map_leaderboard": "Displays a map's leaderboard\n\nThe *map_url* field is the url of the beatmap you want to see the leaderboard of\n\nThe *map_id* field is the map id of the beatmap you want to see the leaderboard of\n\nOnly enter the map url or map id, not both\n\nThe *sort_by_acc* field can be set to True to sort the leaderboard by the best accuracies\n\nThe *sort_reverse* field can be set to True to reverse the default order of the leaderboard, this also works with *sort_by_acc*\n\nDo note that the scores on this leaderboard are only users currently registered into the system",
            "leaderboard": "Displays ppp leaderboard\n\nOnly users that are linked will be shown on the leaderboard",
            "top": "Displays top plays\n\nThe *user* field is where you can enter in an osu! username to see that player's top ppp plays, however the user must have a linked account to be able to see their top plays\n\nThe *sort_by_stars* field can be set to True to sort the top plays by stars instead of ppp\n\nThe *sort_reverse* field can be set to True to reverse the default order of the leaderboard, this also works with *sort_by_stars*"
        }

class Help(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot;
    
    @app_commands.command(name="help", description="Get command list or help with a specific command")
    @app_commands.describe(command="Command to get more info on")
    async def help(self, interaction: discord.Interaction, command:str = None):
        # Specific command chosen
        if command:
            if len(command) > 1:
                if command[0] == '/':
                    command = command[1:]
                if command in commands_list_detailed:
                    embed = discord.Embed(
                        title=f"/{command} Details",
                        description=f"{commands_list_detailed[command]}",
                        color=discord.Color.blue()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            embed = discord.Embed(
                title="Invalid Command",
                description=f"**{command}** is not a valid command, do **/help** to see the list of valid commands",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        else:
            # Listing all commands
            pages: list[discord.Embed] = []
            keys = list(commands_list.keys())
            for i in range(0, len(keys), 5):
                chunk = keys[i:i+5]
                lines = [f"**/{cmd}**\n\u00A0\u00A0\u00A0\u00A0{commands_list[cmd]}" for cmd in chunk]
                embed = discord.Embed(
                    title="Command List",
                    description="\n".join(lines),
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Page {(i // 5) + 1} of {(len(keys) - 1) // 5 + 1}")
                pages.append(embed)

            view = PageView(user_id=interaction.user.id, pages=pages)
            await interaction.response.send_message(embed=pages[0], view=view, ephemeral=True)
            print_to_console(f"User {interaction.user.id}'s help request was successful")
            return
        
async def setup(bot):
    await bot.add_cog(Help(bot))