import discord
from discord import app_commands
from discord.ext import commands
from utils.database import db
from utils.embeds import EmbedBuilder

class VerificationCog(commands.Cog):
    """Configurable reaction role verification with auto‑mute for new members."""

    def __init__(self, bot):
        self.bot = bot

    # ---------- Database helpers ----------
    async def get_settings(self, guild_id: int):
        return await db.database.verification_settings.find_one({"guild_id": guild_id})

    async def update_settings(self, guild_id: int, key: str, value):
        await db.database.verification_settings.update_one(
            {"guild_id": guild_id},
            {"$set": {key: value}},
            upsert=True
        )

    # ---------- Auto‑mute new members with permission setup ----------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Give the Muted role to every new member until they verify."""
        settings = await self.get_settings(member.guild.id)
        if not settings:
            return  # verification not set up in this server

        # Find or create the Muted role
        muted_role = discord.utils.get(member.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await member.guild.create_role(name="Muted", reason="Auto‑mute new members")
            # Apply send_messages = False to all categories and text channels
            for category in member.guild.categories:
                try:
                    await category.set_permissions(muted_role, send_messages=False, add_reactions=False)
                except:
                    pass
            for channel in member.guild.text_channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                except:
                    pass

        try:
            await member.add_roles(muted_role, reason="New member – needs verification")
        except:
            pass

    # ---------- Slash commands for configuration ----------
    verify = app_commands.Group(name="verify", description="Configure reaction role verification")

    @verify.command(name="set_channel", description="Set the channel where the verification message will be posted")
    @app_commands.default_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.update_settings(interaction.guild_id, "channel_id", channel.id)
        embed = EmbedBuilder.success(interaction.user, "Verification channel set", f"Channel: {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="set_role", description="Set the role to assign when a user verifies (optional)")
    @app_commands.default_permissions(administrator=True)
    async def set_role(self, interaction: discord.Interaction, role: discord.Role):
        await self.update_settings(interaction.guild_id, "role_id", role.id)
        embed = EmbedBuilder.success(interaction.user, "Verification role set", f"Role: {role.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="set_emoji", description="Set the emoji to react with (default: ✅)")
    @app_commands.default_permissions(administrator=True)
    async def set_emoji(self, interaction: discord.Interaction, emoji: str):
        await self.update_settings(interaction.guild_id, "emoji", emoji)
        embed = EmbedBuilder.success(interaction.user, "Verification emoji set", f"Emoji: {emoji}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @verify.command(name="create", description="Create the verification message in the configured channel")
    @app_commands.default_permissions(administrator=True)
    async def create_message(self, interaction: discord.Interaction,
                            title: str = "Verification Required",
                            description: str = "React with the emoji below to gain access to the server."):
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

        embed_msg = discord.Embed(title=title, description=description, color=discord.Color.green())
        emoji = settings.get("emoji", "✅")
        msg = await channel.send(embed=embed_msg)
        await msg.add_reaction(emoji)

        await self.update_settings(interaction.guild_id, "message_id", msg.id)
        response_embed = EmbedBuilder.success(interaction.user, "Verification message created", f"Posted in {channel.mention}")
        await interaction.response.send_message(embed=response_embed, ephemeral=True)

    @verify.command(name="setup_mute", description="Apply Muted role permissions to all categories and channels (admin only)")
    @app_commands.default_permissions(administrator=True)
    async def setup_mute(self, interaction: discord.Interaction):
        """Manually apply mute permissions to all existing channels (for existing servers)."""
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            await interaction.response.send_message("Muted role not found. It will be created automatically when a new member joins.", ephemeral=True)
            return

        count = 0
        for category in interaction.guild.categories:
            try:
                await category.set_permissions(muted_role, send_messages=False, add_reactions=False)
                count += 1
            except:
                pass
        for channel in interaction.guild.text_channels:
            try:
                await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                count += 1
            except:
                pass
        await interaction.response.send_message(f"✅ Updated {count} categories/channels with Muted role permissions.", ephemeral=True)

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

        desc = f"**Channel:** {channel.mention if channel else 'Not set'}\n"
        desc += f"**Role:** {role.mention if role else 'Not set'}\n"
        desc += f"**Emoji:** {emoji}\n"
        desc += f"**Message ID:** `{msg_id}`"
        embed = EmbedBuilder.info(interaction.user, desc)
        embed.title = "🔧 Verification Settings"
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------- Reaction handler – unmute + give role ----------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        settings = await self.get_settings(payload.guild_id)
        if not settings:
            return

        # Check channel and message IDs
        if payload.channel_id != settings.get("channel_id") or payload.message_id != settings.get("message_id"):
            return

        expected_emoji = settings.get("emoji", "✅")
        if str(payload.emoji) != expected_emoji:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        # 1. Remove Muted role if it exists
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role, reason="Verified via reaction")

        # 2. Add the configured verification role (if any)
        role_id = settings.get("role_id")
        if role_id:
            role = guild.get_role(role_id)
            if role:
                await member.add_roles(role, reason="Reaction role verification")

        # Optional: send a confirmation DM
        try:
            await member.send(f"✅ You have been verified in **{guild.name}**.")
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """(Optional) Remove role if reaction is removed – left empty by design."""
        pass

async def setup(bot):
    await bot.add_cog(VerificationCog(bot))