from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR  = BASE_DIR / "database" / "storage"