import discord
from discord import app_commands
from discord.ext import commands
from utils.database import db
from utils.embeds import EmbedBuilder

class VerificationCog(commands.Cog):
    """Configurable reaction role verification system."""

    def __init__(self, bot):
        self.bot = bot

    # Helper function to get settings for a guild
    async def get_settings(self, guild_id: int):
        return await db.database.verification_settings.find_one({"guild_id": guild_id})

    async def update_settings(self, guild_id: int, key: str, value):
        await db.database.verification_settings.update_one(
            {"guild_id": guild_id},
            {"$set": {key: value}},
            upsert=True
        )

    # ---------- Slash Commands Group ----------
    verify = app_commands.Group(name="verify", description="Configure reaction role verification")

    @verify.command(name="set_channel", description="Set the channel where the verification message will be posted")
    @app_commands.default_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.update_settings(interaction.guild_id, "channel_id", channel.id)
        embed = EmbedBuilder.success(interaction.user, "Verification channel set", f"Channel: {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="set_role", description="Set the role to assign when a user verifies")
    @app_commands.default_permissions(administrator=True)
    async def set_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.update_settings(interaction.guild_id, "role_id", role.id)
        embed = EmbedBuilder.success(interaction.user, "Verification role set", f"Role: {role.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="set_emoji", description="Set the emoji to react with (default: ✅)")
    @app_commands.default_permissions(administrator=True)
    async def set_emoji(self, interaction: discord.Interaction, emoji: str):
        # Validate emoji (simple check: it should be a single emoji or custom emoji string)
        await self.update_settings(interaction.guild_id, "emoji", emoji)
        embed = EmbedBuilder.success(interaction.user, "Verification emoji set", f"Emoji: {emoji}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="create", description="Create the verification message in the configured channel")
    @app_commands.default_permissions(administrator=True)
    async def create_message(self, interaction: discord.Interaction, title: str = "Verification Required", description: str = "React with the emoji below to gain access to the server."):
        settings = await self.get_settings(interaction.guild_id)
        if not settings or "channel_id" not in settings:
            embed = EmbedBuilder.error(interaction.user, "Please set a verification channel first using `/verify set_channel`.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel = interaction.guild.get_channel(settings["channel_id"])
        if not channel:
            embed = EmbedBuilder.error(interaction.user, "Configured channel not found. Please set a valid channel.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        emoji = settings.get("emoji", "✅")
        msg = await channel.send(embed=embed)
        await msg.add_reaction(emoji)

        # Store the message ID
        await self.update_settings(interaction.guild_id, "message_id", msg.id)

        response_embed = EmbedBuilder.success(interaction.user, "Verification message created", f"Posted in {channel.mention}")
        await interaction.response.send_message(embed=response_embed, ephemeral=True)

    @verify.command(name="disable", description="Disable verification for this server")
    @app_commands.default_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        await db.database.verification_settings.delete_one({"guild_id": interaction.guild_id})
        embed = EmbedBuilder.success(interaction.user, "Verification disabled", "You can set it up again anytime.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="status", description="View current verification settings")
    @app_commands.default_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction):
        settings = await self.get_settings(interaction.guild_id)
        if not settings:
            embed = EmbedBuilder.info(interaction.user, "Verification not configured.\nUse `/verify set_channel`, `/verify set_role`, then `/verify create`.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel = interaction.guild.get_channel(settings.get("channel_id")) if settings.get("channel_id") else None
        role = interaction.guild.get_role(settings.get("role_id")) if settings.get("role_id") else None
        emoji = settings.get("emoji", "✅")
        msg_id = settings.get("message_id", "Not set")

        description = f"**Channel:** {channel.mention if channel else 'Not set'}\n"
        description += f"**Role:** {role.mention if role else 'Not set'}\n"
        description += f"**Emoji:** {emoji}\n"
        description += f"**Message ID:** `{msg_id}`"
        embed = EmbedBuilder.info(interaction.user, description)
        embed.title = "🔧 Verification Settings"
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------- Reaction Handler ----------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        settings = await self.get_settings(payload.guild_id)
        if not settings:
            return
        # Check channel and message
        if payload.channel_id != settings.get("channel_id") or payload.message_id != settings.get("message_id"):
            return
        # Check emoji
        expected_emoji = settings.get("emoji", "✅")
        if str(payload.emoji) != expected_emoji:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        role_id = settings.get("role_id")
        if not role_id:
            return
        role = guild.get_role(role_id)
        if not role:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return

        try:
            await member.add_roles(role, reason="Reaction role verification")
            # Optionally send a DM or log
        except Exception as e:
            # Log error silently or to mod log
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Optional: remove role when reaction is removed
        if payload.user_id == self.bot.user.id:
            return

        settings = await self.get_settings(payload.guild_id)
        if not settings:
            return
        if payload.channel_id != settings.get("channel_id") or payload.message_id != settings.get("message_id"):
            return
        expected_emoji = settings.get("emoji", "✅")
        if str(payload.emoji) != expected_emoji:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        role_id = settings.get("role_id")
        if not role_id:
            return
        role = guild.get_role(role_id)
        if not role:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return

        try:
            await member.remove_roles(role, reason="Removed verification reaction")
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(VerificationCog(bot))