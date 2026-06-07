import discord

def has_mod_permissions(interaction: discord.Interaction) -> bool:
    """Check if user has moderation permissions (kick/ban/manage messages)."""
    perms = interaction.user.guild_permissions
    return perms.kick_members or perms.ban_members or perms.manage_messages

def is_admin(interaction: discord.Interaction) -> bool:
    """Check if user is administrator."""
    return interaction.user.guild_permissions.administrator
