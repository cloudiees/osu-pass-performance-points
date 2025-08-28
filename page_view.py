import discord

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
    async def prev_pg(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = self.current - 1
        if self.current < 0:
            self.current = 0
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
        
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_pg(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = self.current + 1
        if self.current >= len(self.pages):
            self.current = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)