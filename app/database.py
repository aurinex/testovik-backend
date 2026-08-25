from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

users = db.users
tasks = db.tasks
results = db.results
groups = db.groups


async def ping() -> None:
    await client.admin.command("ping")