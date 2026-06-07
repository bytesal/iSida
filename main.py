import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from utils.database import db
from utils.anti_spam import AntiSpamHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('iSida')

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Required for anti-spam/link/mention detection
intents.members = True          # Required for member-specific actions

class iSidaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),  # Fallback, but only slash commands used
            intents=intents,
            help_command=None  # Custom help command will be provided
        )
        self.db = None
        self.anti_spam = None

    async def setup_hook(self):
        """Initialize database, cogs, and anti-spam handler before bot starts."""
        # Connect to MongoDB
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in environment variables")
        
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        db.client = self.mongo_client
        db.database = self.mongo_client['iSidaDB']  # Database name
        
        # Initialize anti-spam handler
        self.anti_spam = AntiSpamHandler(self)
        
        # Load all cogs
        await self.load_extension('cogs.moderation')
        await self.load_extension('cogs.help')
        await self.load_extension('cogs.sticky')
        logger.info("Loaded cogs: moderation, help, sticky")
        
        # Sync slash commands with Discord
        await self.tree.sync()
        logger.info("Synced slash commands")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name="/help | iSida"))

    async def on_message(self, message):
        """Global message handler for anti-spam, anti-link, anti-mass-mention."""
        # Ignore bot's own messages and DMs
        if message.author.bot or not message.guild:
            return
        
        # Process anti-spam, link, mention protections
        await self.anti_spam.process_message(message)
        
        # Ensure commands still work (if any prefix commands, but we ignore here)
        await self.process_commands(message)

    async def close(self):
        """Clean up MongoDB connection on shutdown."""
        await self.mongo_client.close()
        await super().close()

# Run bot
bot = iSidaBot()
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

bot.run(token)
