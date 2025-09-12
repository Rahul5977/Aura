from prisma import Prisma
from typing import AsyncGenerator
import asyncio
from app.core.config import settings

# Global Prisma client instance
prisma = Prisma()

async def connect_database():
    """
    Connect to the database.
    
    This function establishes a connection to the PostgreSQL database
    using Prisma ORM. Should be called during application startup.
    """
    try:
        await prisma.connect()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

async def disconnect_database():
    """
    Disconnect from the database.
    
    This function closes the database connection.
    Should be called during application shutdown.
    """
    try:
        await prisma.disconnect()
        print("✅ Database disconnected successfully")
    except Exception as e:
        print(f"❌ Database disconnection failed: {e}")

async def get_database() -> AsyncGenerator[Prisma, None]:
    """
    Get database session for dependency injection.
    
    Yields:
        Prisma client instance
    """
    yield prisma