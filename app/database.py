from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("pfe_transplantation")

# Create MongoDB client (SYNC)
client = MongoClient("mongodb://localhost:27017")

# Select database
db = client["pfe_transplantation"]
