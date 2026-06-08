import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available slash commands.")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            # Get all top-level commands (including groups)
            commands_list = self.bot.tree.get_commands()

            categorized = {}
            for cmd in commands_list:
                # Determine cog name
                cog_name = "General"
                if hasattr(cmd, 'callback') and cmd.callback and hasattr(cmd.callback, '__module__'):
                    module = cmd.callback.__module__
                    if module.startswith('cogs.'):
                        cog_name = module.split('.')[1].capitalize()

                # Build display lines for this command
                if isinstance(cmd, app_commands.Group):
                    # For groups, list all subcommands as separate lines
                    display_lines = []
                    for sub in cmd.commands:
                        display_lines.append(f"`/{cmd.name} {sub.name}` - {sub.description}")
                    cmd_display = "\n".join(display_lines)
                else:
                    cmd_display = f"`/{cmd.name}` - {cmd.description}"

                if cog_name not in categorized:
                    categorized[cog_name] = []
                categorized[cog_name].append(cmd_display)

            embed = discord.Embed(
                title="📖 iSida Help",
                description="All slash commands are listed below.",
                color=discord.Color.blue()
            )

            for cog, entries in sorted(categorized.items()):
                full_text = "\n".join(entries)
                if len(full_text) > 1024:
                    full_text = full_text[:1000] + "\n*...and more*"
                embed.add_field(name=f"**{cog}**", value=full_text or "No commands", inline=False)

            embed.set_footer(text="Use /command - All commands are slash commands only.")
            await interaction.edit_original_response(embed=embed)

        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred: {e}", embed=None)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))