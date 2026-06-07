"""Global database connection handler."""
from motor.motor_asyncio import AsyncIOMotorDatabase

class Database:
    client = None
    database: AsyncIOMotorDatabase = None

db = Database()
