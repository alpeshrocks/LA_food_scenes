import os
from dotenv import load_dotenv
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "la-food-scenes/0.1")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEOCODER = os.getenv("GEOCODER", "nominatim").lower()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
