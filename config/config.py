# Imports
from dotenv import load_dotenv
from pathlib import Path
from fastapi_mail import ConnectionConfig
import os

# Load environment variables
load_dotenv()

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR  = BASE_DIR / "database" / "storage"

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_bad_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Mail config
MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=(os.getenv("MAIL_STARTTLS", "True") == "True"),
    MAIL_SSL_TLS=(os.getenv("MAIL_SSL_TLS", "False") == "True"),
    USE_CREDENTIALS=True
)