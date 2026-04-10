import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fitfusion")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]


def get_profiles_collection():
    return db["profiles"]


def get_tasks_collection():
    return db["tasks"]
