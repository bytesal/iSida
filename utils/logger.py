from utils.database import db
from utils.embeds import EmbedBuilder

async def log_to_mod_channel(bot, guild, action, moderator, target, details, warning_id=None):
    """Send a detailed embed to the guild's configured mod log channel."""
    config = await db.database.guild_configs.find_one({"_id": guild.id})
    if not config or not config.get("mod_log_channel"):
        return  # No mod log channel set
    
    channel = guild.get_channel(config["mod_log_channel"])
    if not channel:
        return
    
    # Build embed
    embed = EmbedBuilder.log(
        title=f"📋 {action}",
        description=details,
        color=discord.Color.dark_red() if "Ban" in action or "Kick" in action else discord.Color.orange()
    )
    embed.add_field(name="Moderator", value=moderator.mention, inline=True)
    embed.add_field(name="Target", value=target.mention if target else "None", inline=True)
    if warning_id:
        embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=True)
    embed.set_footer(text=f"Action ID: {action.lower().replace(' ', '_')}")
    
    await channel.send(embed=embed)

import discord
