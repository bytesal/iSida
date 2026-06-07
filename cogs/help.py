import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    """Provides a dynamic help command listing all slash commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available slash commands.")
    async def help_command(self, interaction: discord.Interaction):
        """Display a categorized list of all slash commands."""
        # Get all global commands
        commands_list = await self.bot.tree.fetch_commands()
        
        # Categorize commands by their cog name (from the command's callback's __module__)
        categorized = {}
        for cmd in commands_list:
            # Find the actual command object in the bot's tree
            app_cmd = self.bot.tree.get_command(cmd.name)
            if app_cmd and app_cmd.callback:
                module = app_cmd.callback.__module__
                # Extract cog name: 'cogs.moderation' -> 'Moderation'
                if module.startswith('cogs.'):
                    cog_name = module.split('.')[1].capitalize()
                else:
                    cog_name = "General"
            else:
                cog_name = "General"
            
            if cog_name not in categorized:
                categorized[cog_name] = []
            categorized[cog_name].append(cmd)
        
        embed = discord.Embed(
            title="📖 iSida Help",
            description="All slash commands are listed below.",
            color=discord.Color.blue()
        )
        
        for cog, cmds in sorted(categorized.items()):
            cmd_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in cmds])
            embed.add_field(name=f"**{cog}**", value=cmd_list or "No commands", inline=False)
        
        embed.set_footer(text="Use /command - All commands are slash commands only.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
