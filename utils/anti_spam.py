import re
import discord
from collections import defaultdict
from datetime import datetime, timedelta
from utils.embeds import EmbedBuilder
from utils.logger import log_to_mod_channel

class AntiSpamHandler:
    """Handles anti-spam, anti-link, and anti-mass-mention enforcement."""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_records = defaultdict(list)  # guild_id: {user_id: [timestamps]}
        self.spam_threshold = 5     # messages
        self.spam_interval = 5      # seconds
        self.mention_limit = 5
        # Discord invite regex (simplified)
        self.invite_pattern = re.compile(r'(discord\.(gg|me|io|com/invite)/[a-zA-Z0-9]+)', re.IGNORECASE)

    async def process_message(self, message: discord.Message):
        """Check a single message for violations."""
        guild = message.guild
        author = message.author
        
        # Skip bot owners or users with manage_messages permission (immune)
        if author.guild_permissions.manage_messages:
            return
        
        # Record timestamp
        now = datetime.utcnow()
        self.message_records[guild.id].append((author.id, now))
        # Clean old records
        self.message_records[guild.id] = [(uid, ts) for uid, ts in self.message_records[guild.id] if ts > now - timedelta(seconds=self.spam_interval)]
        
        # Count messages from this user in the interval
        user_messages = [ts for uid, ts in self.message_records[guild.id] if uid == author.id]
        
        # --- Anti-spam ---
        if len(user_messages) > self.spam_threshold:
            await self.punish(message, "Spamming", "You are sending messages too quickly.")
            return
        
        # --- Anti-link (Discord invites) ---
        if self.invite_pattern.search(message.content):
            await self.punish(message, "Posting invite links", "Discord invite links are not allowed.")
            return
        
        # --- Anti-mass-mention ---
        mention_count = len(message.mentions) + len(message.role_mentions) + (1 if message.mention_everyone else 0)
        if mention_count > self.mention_limit:
            await self.punish(message, f"Mass mentioning ({mention_count} mentions)", f"Please do not mention more than {self.mention_limit} users/roles.")
            return

    async def punish(self, message: discord.Message, reason: str, user_friendly_msg: str):
        """Delete violating message, DM the user, and log to mod channel."""
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        
        # Send a temporary warning embed in the channel
        embed = EmbedBuilder.warning(message.author, f"Message removed: {reason}", user_friendly_msg)
        warning_msg = await message.channel.send(embed=embed, delete_after=5)
        
        # DM the user (if possible)
        try:
            dm_embed = discord.Embed(title="⚠️ Warning", description=f"You violated a rule in **{message.guild.name}**.\n**Action:** {reason}\n{user_friendly_msg}", color=discord.Color.orange())
            await message.author.send(embed=dm_embed)
        except:
            pass
        
        # Log to mod channel
        await log_to_mod_channel(
            self.bot, message.guild, "Auto-Mod Violation",
            self.bot.user, message.author,
            f"**Action:** {reason}\n**Message Content:** {message.content[:500]}"
        )
