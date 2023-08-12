from pathlib import Path
from types import SimpleNamespace as Dict

# Root Path
BASE_DIR = Path(__file__).parent

# Define the path to the 'static' directory
STATIC_DIR = BASE_DIR / "static"

# Configuration for Peewee ORM
DATABASE = "db.sqlite3"

# Core
DEBUG = True
SECRET_KEY = "your_secret_key"

# Authentication
SECRET_ALGORITHM = "HS256"
SECRET_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# API (Roles)
ROLE_USER = 3
ROLE_PUBLIC = 2
ROLES = {
    1: Dict(name="developer", perms=[]),
    2: Dict(name="public", perms=[]),
    3: Dict(name="user", perms=[]),
}

# API (User)
USER_SCHEMA = {
    "role_id": ROLE_PUBLIC,
    "is_authenticated": False,
    "id": None,
    "username": None,
    "email": None,
    "password": None,
    "first_name": None,
    "last_name": None,
    "middle_name": None,
    "is_superuser": None,
    "is_staff": None,
    "is_active": None,
    "date_joined": None,
    "last_login": None,
}
