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
intents.reactions = True        # Required for reaction role

class iSidaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            help_command=None
        )
        self.mongo_client = None
        self.anti_spam = None

    async def setup_hook(self):
        """Initialize database, cogs, and anti-spam handler before bot starts."""
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in environment variables")
        
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        db.client = self.mongo_client
        db.database = self.mongo_client['iSidaDB']
        
        self.anti_spam = AntiSpamHandler(self)
        
        # Load all cogs
        await self.load_extension('cogs.moderation')
        await self.load_extension('cogs.help')
        await self.load_extension('cogs.sticky')
        await self.load_extension('cogs.verification')
        await self.load_extension('cogs.transcripts')
        logger.info("Loaded cogs: moderation, help, sticky, verification, transcripts")
        
        await self.tree.sync()
        logger.info("Synced slash commands")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name="/help | iSida"))

    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        await self.anti_spam.process_message(message)
        await self.process_commands(message)

    async def close(self):
        if self.mongo_client:
            await self.mongo_client.close()
        await super().close()

# Run bot
bot = iSidaBot()
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

bot.run(token)
