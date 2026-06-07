import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    """Dynamic help command listing all slash commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available slash commands.")
    async def help_command(self, interaction: discord.Interaction):
        # Defer the response to avoid timeout (gives us up to 15 minutes)
        await interaction.response.defer(thinking=True)

        # Fetch all global commands from Discord API
        commands_list = await self.bot.tree.fetch_commands()

        categorized = {}
        for cmd in commands_list:
            # Try to get the actual command object to extract cog name
            app_cmd = self.bot.tree.get_command(cmd.name)
            if app_cmd and app_cmd.callback:
                module = app_cmd.callback.__module__
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
            cmd_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in cmds[:10]])  # Limit to 10 per cog
            if len(cmds) > 10:
                cmd_list += f"\n*and {len(cmds)-10} more...*"
            embed.add_field(name=f"**{cog}**", value=cmd_list or "No commands", inline=False)

        embed.set_footer(text="Use /command - All commands are slash commands only.")

        # Edit the deferred response with the embed
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))