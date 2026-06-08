import discord
from datetime import datetime
from utils.database import db
from utils.embeds import EmbedBuilder

async def log_to_mod_channel(bot, guild, action, moderator, target, details, warning_id=None):
    """Send a detailed embed to the guild's configured mod log channel AND store in MongoDB."""
    
    # 1. Store in MongoDB (this creates the 'mod_logs' collection automatically)
    log_entry = {
        "guild_id": guild.id,
        "action": action,
        "moderator_id": moderator.id,
        "moderator_name": str(moderator),
        "target_id": target.id if target else None,
        "target_name": str(target) if target else None,
        "reason": details,
        "timestamp": datetime.utcnow()
    }
    if warning_id:
        log_entry["warning_id"] = warning_id
    
    await db.database.mod_logs.insert_one(log_entry)
    
    # 2. Send to Discord channel if configured
    config = await db.database.guild_configs.find_one({"_id": guild.id})
    if not config or not config.get("mod_log_channel"):
        return
    
    channel = guild.get_channel(config["mod_log_channel"])
    if not channel:
        return
    
    # Build embed for Discord
    embed = EmbedBuilder.log(
        title=f"📋 {action}",
        description=details,
        color=discord.Color.dark_red() if "Ban" in action or "Kick" in action else discord.Color.orange()
    )
    embed.add_field(name="Moderator", value=moderator.mention, inline=True)
    embed.add_field(name="Target", value=target.mention if target else "None", inline=True)
    if warning_id:
        embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=True)
    embed.set_footer(text=f"Action logged at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    
    await channel.send(embed=embed)
