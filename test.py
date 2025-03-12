import os
from dotenv import load_dotenv

load_dotenv()  # Ensure .env is loaded

print("REDIS URL from env:", os.getenv("REDIS_URL"))
