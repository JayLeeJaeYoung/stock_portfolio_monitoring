import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Singleton-style MongoDB client
_client = None

# database.py will be used in models.py to access the database
# This allows for a single connection to be reused across the app


def get_db_connection():
    """
    Returns the MongoDB database instance.
    Reuses the same client across the app.
    """
    global _client
    if _client is None:
        mongodb_uri = os.getenv("MONGODB_URI")
        _client = MongoClient(mongodb_uri, server_api=ServerApi("1"))
    return _client["mydb"]


def is_mongodb_connected():
    """
    Checks if MongoDB is reachable by pinging the server.
    Uses the shared client instance.
    """
    print("Checking MongoDB connection...")
    try:
        get_db_connection().client.admin.command("ping")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False
