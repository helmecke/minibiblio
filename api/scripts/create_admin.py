"""
Script to create default admin user if no users exist.
This script is called automatically during Docker container startup.
"""

import asyncio
import os
import sys

# Add parent directory to path to import api modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
from api.db.database import async_session_factory
from api.db.models import UserDB, UserRole
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password"""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def create_default_admin():
    """Create default admin user if no users exist"""
    async with async_session_factory() as session:
        try:
            # Check if any users exist
            result = await session.execute(select(UserDB))
            existing_users = result.scalars().all()

            if not existing_users:
                # Get credentials from environment or use defaults
                admin_username = os.getenv("ADMIN_USERNAME", "admin")
                admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
                admin_email = os.getenv("ADMIN_EMAIL", "admin@minibiblio.local")

                # Create admin user
                admin = UserDB(
                    username=admin_username,
                    email=admin_email,
                    hashed_password=hash_password(admin_password),
                    is_active=True,
                    role=UserRole.admin,
                )

                session.add(admin)
                await session.commit()

                print(f"✓ Default admin user created: {admin_username}")
                print(f"  Email: {admin_email}")
                print(f"  Password: {admin_password}")
                print()
                print(
                    "  ⚠️  IMPORTANT: Change the default password immediately after first login!"
                )
                print()
            else:
                print("✓ Users already exist in database, skipping admin creation")

        except Exception as e:
            print(f"✗ Error creating admin user: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_default_admin())
