
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.models import User

async def check_admin():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@gestion-rb.com")
        )
        user = result.scalar_one_or_none()
        if user:
            print(f"✅ User found: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Active: {user.is_active}")
        else:
            print("❌ User 'admin@gestion-rb.com' not found.")

if __name__ == "__main__":
    asyncio.run(check_admin())
