import discord
from discord import app_commands
from discord.ext import commands, tasks
from utils.database import db
from utils.embeds import EmbedBuilder

class StickyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_sticky_messages.start()

    def cog_unload(self):
        self.check_sticky_messages.cancel()

    @tasks.loop(seconds=10)
    async def check_sticky_messages(self):
        """Background task to verify sticky messages are still present."""
        async for config in db.database.sticky_messages.find({}):
            guild_id = config["guild_id"]
            channel_id = config["channel_id"]
            message_id = config.get("message_id")
            content = config["content"]

            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            try:
                await channel.fetch_message(message_id)
            except (discord.NotFound, discord.Forbidden):
                # Message is missing – repost it
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="📌 Sticky message")
                new_msg = await channel.send(embed=embed)
                await db.database.sticky_messages.update_one(
                    {"guild_id": guild_id, "channel_id": channel_id},
                    {"$set": {"message_id": new_msg.id}}
                )

    # Slash command group
    sticky = app_commands.Group(name="sticky", description="Manage sticky messages in this channel")

    @sticky.command(name="set", description="Set a sticky message in this channel")
    @app_commands.default_permissions(manage_messages=True)
    async def sticky_set(self, interaction: discord.Interaction, message: str):
        """Set a sticky message that will stay at the bottom of the channel."""
        await db.database.sticky_messages.delete_one({
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id
        })

        embed = discord.Embed(description=message, color=discord.Color.blue())
        embed.set_footer(text="📌 Sticky message – do not delete")
        sticky_msg = await interaction.channel.send(embed=embed)

        await db.database.sticky_messages.insert_one({
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id,
            "message_id": sticky_msg.id,
            "content": message
        })

        response_embed = EmbedBuilder.success(
            interaction.user,
            "Sticky message set",
            f"Message: {message}\nChannel: {interaction.channel.mention}"
        )
        await interaction.response.send_message(embed=response_embed, ephemeral=True)

    @sticky.command(name="remove", description="Remove the sticky message from this channel")
    @app_commands.default_permissions(manage_messages=True)
    async def sticky_remove(self, interaction: discord.Interaction):
        config = await db.database.sticky_messages.find_one({
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id
        })
        if not config:
            embed = EmbedBuilder.error(interaction.user, "No sticky message set in this channel.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            channel = interaction.channel
            msg = await channel.fetch_message(config["message_id"])
            await msg.delete()
        except:
            pass

        await db.database.sticky_messages.delete_one({
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id
        })

        embed = EmbedBuilder.success(interaction.user, "Sticky message removed.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @sticky.command(name="view", description="View the current sticky message in this channel")
    async def sticky_view(self, interaction: discord.Interaction):
        config = await db.database.sticky_messages.find_one({
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id
        })
        if not config:
            embed = EmbedBuilder.error(interaction.user, "No sticky message set in this channel.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📌 Current sticky message",
            description=config["content"],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Channel: #{interaction.channel.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(StickyCog(bot))
