import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Load from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SMARTY_AUTH_ID = os.getenv("SMARTY_AUTH_ID")
SMARTY_AUTH_TOKEN = os.getenv("SMARTY_AUTH_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Smarty API credentials are optional for now
if not SMARTY_AUTH_ID or not SMARTY_AUTH_TOKEN:
    print("Warning: Smarty API credentials not set. Address analysis will use mock data.")
