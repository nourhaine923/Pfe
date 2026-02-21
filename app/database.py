from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Create MongoDB client (SYNC)
client = MongoClient(MONGODB_URL)

# Select database
db = client[DATABASE_NAME]
