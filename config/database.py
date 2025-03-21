from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from config.settings import settings

# Engine for database operations
client = AsyncIOMotorClient(settings.mongo_db_uri)
engine = AIOEngine(client=client, database="nft_platform")


# Engine for database operations while offline
# client = AsyncIOMotorClient('mongodb://localhost:8020/')
# engine = AIOEngine(client=client, database="nft_platform")
