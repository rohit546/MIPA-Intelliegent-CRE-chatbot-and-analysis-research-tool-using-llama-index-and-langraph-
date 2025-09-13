import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Load from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
