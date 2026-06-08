import discord
from discord import app_commands
from discord.ext import commands
from utils.database import db
from utils.embeds import EmbedBuilder
from datetime import datetime

class TranscriptsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="transcript", description="Save the current ticket channel as a transcript")
    @app_commands.default_permissions(manage_messages=True)
    async def transcript_save(self, interaction: discord.Interaction, title: str = "Ticket Transcript"):
        """Save the entire channel history as a transcript in MongoDB."""
        await interaction.response.defer(thinking=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.edit_original_response(content="This command can only be used in text channels.")
            return

        # Fetch message history (limit 500 to avoid performance issues)
        messages = []
        async for msg in channel.history(limit=500, oldest_first=True):
            messages.append(msg)

        if not messages:
            await interaction.edit_original_response(content="No messages found in this channel.")
            return

        # Build transcript text
        transcript_lines = []
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = f"{msg.author.name}#{msg.author.discriminator}" if msg.author.discriminator != "0" else msg.author.name
            content = msg.clean_content or "[No text]"
            transcript_lines.append(f"[{timestamp}] {author}: {content}")
            # Add attachments info if any
            if msg.attachments:
                attachments = ", ".join([a.url for a in msg.attachments])
                transcript_lines.append(f"  ↳ Attachments: {attachments}")

        transcript_text = "\n".join(transcript_lines)

        # Store in MongoDB
        transcript_doc = {
            "guild_id": interaction.guild_id,
            "channel_id": channel.id,
            "channel_name": channel.name,
            "ticket_title": title,
            "created_by": interaction.user.id,
            "created_by_name": str(interaction.user),
            "created_at": datetime.utcnow(),
            "message_count": len(messages),
            "content": transcript_text
        }
        result = await db.database.ticket_transcripts.insert_one(transcript_doc)

        embed = EmbedBuilder.success(
            interaction.user,
            "Transcript Saved",
            f"Ticket '{title}' saved with ID: `{result.inserted_id}`\n"
            f"Messages: {len(messages)}"
        )
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(TranscriptsCog(bot))
