from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings

MONGO_URI = settings.MONGO_URI
DB_NAME = "navflow"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
cameras_collection = db["cameras"]

def verify_mongo_connection():
    try:
        client.admin.command('ismaster')
        print("MongoDB connection successful!")
        return True
    except ConnectionFailure:
        print("MongoDB connection failed!")
        return False