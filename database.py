from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
from os import getenv

load_dotenv()

client = AsyncIOMotorClient(getenv("MONGO_URL"))
database = client["mydatabase"]

user_collection = database["users"]