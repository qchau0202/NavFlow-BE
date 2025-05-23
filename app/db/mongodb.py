from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb+srv://523k0002:fkOTYrcfC63G9aqA@navflow.nmv5bin.mongodb.net/"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.navflow