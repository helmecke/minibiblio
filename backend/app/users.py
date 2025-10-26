from typing import Dict

from .security import get_password_hash


def _build_user_db() -> Dict[str, dict]:
    # Pre-seeded demo users; replace with a proper persistence layer.
    return {
        "patron": {
            "username": "patron",
            "full_name": "Demo Patron",
            "hashed_password": get_password_hash("patron123"),
            "is_admin": False,
            "scopes": ["user"],
        },
        "librarian": {
            "username": "librarian",
            "full_name": "Demo Librarian",
            "hashed_password": get_password_hash("library123"),
            "is_admin": True,
            "scopes": ["user", "admin"],
        },
    }


USER_DB = _build_user_db()
