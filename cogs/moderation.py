import discord
from discord import app_commands
from discord.ext import commands
from bson import ObjectId
from datetime import datetime
from utils.embeds import EmbedBuilder
from utils.database import db
from utils.permissions import has_mod_permissions, is_admin
from utils.logger import log_to_mod_channel
import asyncio

class ModerationCog(commands.GroupCog, name="moderation"):
    """All moderation commands for iSida."""
    
    def __init__(self, bot):
        self.bot = bot

    # ---------- Helper Methods ----------
    async def get_guild_config(self, guild_id: int):
        """Retrieve guild-specific configuration (e.g., mod log channel)."""
        config = await db.database.guild_configs.find_one({"_id": guild_id})
        if not config:
            config = {"_id": guild_id, "mod_log_channel": None}
            await db.database.guild_configs.insert_one(config)
        return config

    async def set_mod_log_channel(self, guild_id: int, channel_id: int):
        """Set the moderation log channel for a guild."""
        await db.database.guild_configs.update_one(
            {"_id": guild_id},
            {"$set": {"mod_log_channel": channel_id}},
            upsert=True
        )

    # ---------- Slash Commands ----------
    @app_commands.command(name="setmodlog", description="Set the channel where moderation actions will be logged.")
    @app_commands.default_permissions(administrator=True)
    async def setmodlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Admin command to set the mod log channel."""
        await self.set_mod_log_channel(interaction.guild_id, channel.id)
        embed = EmbedBuilder.success(interaction.user, f"Mod log channel set to {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a member."""
        if not interaction.user.guild_permissions.kick_members:
            embed = EmbedBuilder.error(interaction.user, "You do not have permission to kick members.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.kick(reason=reason)
            embed = EmbedBuilder.success(interaction.user, f"Kicked {member.mention}", f"Reason: {reason}")
            await interaction.response.send_message(embed=embed)
            
            # Log action
            await log_to_mod_channel(self.bot, interaction.guild, "Kick", interaction.user, member, reason)
        except discord.Forbidden:
            embed = EmbedBuilder.error(interaction.user, "I don't have permission to kick that member.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.User, reason: str = "No reason provided", delete_message_days: int = 0):
        """Ban a user (by ID or mention)."""
        if not interaction.user.guild_permissions.ban_members:
            embed = EmbedBuilder.error(interaction.user, "You do not have permission to ban members.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await interaction.guild.ban(member, reason=reason, delete_message_days=delete_message_days)
            embed = EmbedBuilder.success(interaction.user, f"Banned {member.mention}", f"Reason: {reason}\nDeleted messages from last {delete_message_days} days.")
            await interaction.response.send_message(embed=embed)
            
            await log_to_mod_channel(self.bot, interaction.guild, "Ban", interaction.user, member, reason)
        except discord.Forbidden:
            embed = EmbedBuilder.error(interaction.user, "I don't have permission to ban that user.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by ID.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Unban a user using their ID."""
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            embed = EmbedBuilder.success(interaction.user, f"Unbanned {user.mention}", f"Reason: {reason}")
            await interaction.response.send_message(embed=embed)
            
            await log_to_mod_channel(self.bot, interaction.guild, "Unban", interaction.user, user, reason)
        except discord.NotFound:
            embed = EmbedBuilder.error(interaction.user, "User not found or not banned.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            embed = EmbedBuilder.error(interaction.user, "Invalid user ID. Please provide a numeric ID.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="warn", description="Warn a member and log the warning.")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Issue a warning to a member."""
        warning = {
            "_id": ObjectId(),
            "guild_id": interaction.guild_id,
            "user_id": member.id,
            "moderator_id": interaction.user.id,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
        await db.database.warnings.insert_one(warning)
        
        embed = EmbedBuilder.warning(interaction.user, f"Warned {member.mention}", f"Reason: {reason}\nWarning ID: `{warning['_id']}`")
        await interaction.response.send_message(embed=embed)
        
        await log_to_mod_channel(self.bot, interaction.guild, "Warn", interaction.user, member, reason, warning_id=str(warning['_id']))

    @app_commands.command(name="removewarn", description="Remove a warning by its ID.")
    @app_commands.default_permissions(moderate_members=True)
    async def removewarn(self, interaction: discord.Interaction, warning_id: str):
        """Delete a specific warning using its MongoDB ObjectId."""
        try:
            result = await db.database.warnings.delete_one({"_id": ObjectId(warning_id), "guild_id": interaction.guild_id})
            if result.deleted_count == 0:
                embed = EmbedBuilder.error(interaction.user, "Warning ID not found in this server.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = EmbedBuilder.success(interaction.user, f"Removed warning `{warning_id}`")
            await interaction.response.send_message(embed=embed)
            
            await log_to_mod_channel(self.bot, interaction.guild, "Remove Warning", interaction.user, None, f"Warning ID {warning_id} removed.")
        except Exception:
            embed = EmbedBuilder.error(interaction.user, "Invalid warning ID format.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="warnings", description="List all warnings for a member.")
    @app_commands.default_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Display all warnings for a specific user."""
        warnings_cursor = db.database.warnings.find({"guild_id": interaction.guild_id, "user_id": member.id})
        warnings_list = await warnings_cursor.to_list(length=100)
        
        if not warnings_list:
            embed = EmbedBuilder.info(interaction.user, f"No warnings found for {member.mention}")
            return await interaction.response.send_message(embed=embed)
        
        description = ""
        for w in warnings_list:
            mod = self.bot.get_user(w['moderator_id']) or f"Unknown ({w['moderator_id']})"
            timestamp = w['timestamp'].strftime("%Y-%m-%d %H:%M UTC")
            description += f"**ID:** `{w['_id']}` | **By:** {mod}\n**Reason:** {w['reason']}\n**Date:** {timestamp}\n\n"
        
        embed = discord.Embed(title=f"Warnings for {member}", description=description[:4000], color=discord.Color.orange())
        embed.set_footer(text=f"Total: {len(warnings_list)}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Delete a number of messages from the channel (optionally filter by member).")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        """Clear messages (max 100)."""
        if amount < 1 or amount > 100:
            embed = EmbedBuilder.error(interaction.user, "Amount must be between 1 and 100.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        def check(msg):
            return member is None or msg.author == member
        
        deleted = await interaction.channel.purge(limit=amount, check=check)
        embed = EmbedBuilder.success(interaction.user, f"Deleted {len(deleted)} messages.")
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        await log_to_mod_channel(self.bot, interaction.guild, "Clear", interaction.user, None, f"Deleted {len(deleted)} messages in #{interaction.channel.name}")

    @app_commands.command(name="slowmode", description="Set slowmode delay in seconds for this channel (0 to disable).")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """Set channel slowmode."""
        if seconds < 0 or seconds > 21600:
            embed = EmbedBuilder.error(interaction.user, "Slowmode must be between 0 and 21600 seconds (6 hours).")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = EmbedBuilder.success(interaction.user, "Slowmode disabled.")
        else:
            embed = EmbedBuilder.success(interaction.user, f"Slowmode set to {seconds} seconds.")
        await interaction.response.send_message(embed=embed)
        
        await log_to_mod_channel(self.bot, interaction.guild, "Slowmode", interaction.user, None, f"Set slowmode to {seconds}s in #{interaction.channel.name}")

    @app_commands.command(name="lockdown", description="Lock the channel (prevent @everyone from sending messages).")
    @app_commands.default_permissions(manage_channels=True)
    async def lockdown(self, interaction: discord.Interaction):
        """Lock the current channel."""
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        
        embed = EmbedBuilder.warning(interaction.user, f"🔒 Channel locked: {interaction.channel.mention}", "Only staff can now send messages.")
        await interaction.response.send_message(embed=embed)
        
        await log_to_mod_channel(self.bot, interaction.guild, "Lockdown", interaction.user, None, f"Locked #{interaction.channel.name}")

    @app_commands.command(name="unlock", description="Unlock the channel (restore @everyone send permissions).")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        """Unlock the current channel."""
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None  # Reset to default
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        
        embed = EmbedBuilder.success(interaction.user, f"🔓 Channel unlocked: {interaction.channel.mention}", "Members can now send messages again.")
        await interaction.response.send_message(embed=embed)
        
        await log_to_mod_channel(self.bot, interaction.guild, "Unlock", interaction.user, None, f"Unlocked #{interaction.channel.name}")

    # ---------- Help Command (dynamic) ----------
    @app_commands.command(name="help", description="Show all available commands.")
    async def help(self, interaction: discord.Interaction):
        """Display a categorized list of all slash commands."""
        commands = self.bot.tree.get_commands()
        # Group commands by cog (module)
        categorized = {}
        for cmd in commands:
            cog_name = cmd.module.split('.')[-1] if cmd.module else "General"
            if cog_name not in categorized:
                categorized[cog_name] = []
            categorized[cog_name].append(cmd)
        
        embed = discord.Embed(title="📖 iSida Help", description="All slash commands are listed below.", color=discord.Color.blue())
        for cog, cmds in categorized.items():
            cmd_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in cmds])
            embed.add_field(name=f"**{cog.title()}**", value=cmd_list or "No commands", inline=False)
        
        embed.set_footer(text="Use /command - All commands are slash commands only.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
