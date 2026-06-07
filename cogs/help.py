import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available slash commands.")
    async def help_command(self, interaction: discord.Interaction):
        # Defer response to avoid timeout
        await interaction.response.defer(thinking=True)

        try:
            # Use locally cached commands (instant, no API call)
            commands_list = self.bot.tree.get_commands()

            categorized = {}
            for cmd in commands_list:
                cog_name = "General"
                if cmd.callback and cmd.callback.__module__:
                    module = cmd.callback.__module__
                    if module.startswith('cogs.'):
                        cog_name = module.split('.')[1].capitalize()
                if cog_name not in categorized:
                    categorized[cog_name] = []
                categorized[cog_name].append(cmd)

            embed = discord.Embed(
                title="📖 iSida Help",
                description="All slash commands are listed below.",
                color=discord.Color.blue()
            )

            for cog, cmds in sorted(categorized.items()):
                # Limit each field to 1024 chars to avoid Discord error
                cmd_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in cmds])
                if len(cmd_list) > 1024:
                    cmd_list = cmd_list[:1000] + "\n*...and more*"
                embed.add_field(name=f"**{cog}**", value=cmd_list or "No commands", inline=False)

            embed.set_footer(text="Use /command - All commands are slash commands only.")
            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred: {e}", embed=None)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))