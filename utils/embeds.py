import discord

class EmbedBuilder:
    """Consistent embed generation for all bot responses."""
    
    @staticmethod
    def _base_embed(title: str, color: discord.Color, description: str = None) -> discord.Embed:
        embed = discord.Embed(title=title, color=color)
        if description:
            embed.description = description
        embed.set_footer(text="iSida Moderation Bot")
        return embed

    @staticmethod
    def success(user: discord.User, title: str, description: str = None) -> discord.Embed:
        embed = EmbedBuilder._base_embed(f"✅ {title}", discord.Color.green(), description)
        embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else None)
        return embed

    @staticmethod
    def error(user: discord.User, description: str) -> discord.Embed:
        embed = EmbedBuilder._base_embed("❌ Error", discord.Color.red(), description)
        embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else None)
        return embed

    @staticmethod
    def warning(user: discord.User, title: str, description: str = None) -> discord.Embed:
        embed = EmbedBuilder._base_embed(f"⚠️ {title}", discord.Color.orange(), description)
        embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else None)
        return embed

    @staticmethod
    def info(user: discord.User, description: str) -> discord.Embed:
        embed = EmbedBuilder._base_embed("ℹ️ Information", discord.Color.blue(), description)
        embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else None)
        return embed

    @staticmethod
    def log(title: str, description: str, color: discord.Color = discord.Color.dark_grey()) -> discord.Embed:
        """Special embed for moderation logs."""
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.utcnow())
        embed.set_footer(text="iSida Mod Log")
        return embed

from datetime import datetime
