import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import db_config
from app.utils.logger import logger
from typing import Optional

# Global database instances
client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None


async def init_database() -> None:
    """Initialize MongoDB connection"""
    global client, database

    try:
        if not db_config.mongodb_url:
            logger.warning("MongoDB URL not configured, skipping database initialization")
            return

        logger.info("Initializing MongoDB connection", extra={"extra_data": {
            "database_name": db_config.mongodb_database_name,
            "min_pool_size": db_config.mongodb_min_pool_size,
            "max_pool_size": db_config.mongodb_max_pool_size
        }})

        # Create MongoDB client
        client = AsyncIOMotorClient(
            db_config.connection_string,
            maxPoolSize=db_config.mongodb_max_pool_size,
            minPoolSize=db_config.mongodb_min_pool_size,
            maxIdleTimeMS=db_config.mongodb_max_idle_time_ms,
            serverSelectionTimeoutMS=db_config.mongodb_server_selection_timeout_ms,
            connectTimeoutMS=db_config.mongodb_connect_timeout_ms,
            socketTimeoutMS=db_config.mongodb_socket_timeout_ms,
        )

        # Get database
        database = client[db_config.mongodb_database_name]

        # Test connection
        await client.admin.command('ping')

        logger.info("MongoDB connection established successfully", extra={"extra_data": {
            "database_name": db_config.mongodb_database_name
        }})

    except Exception as e:
        logger.error("Failed to initialize MongoDB connection", extra={"extra_data": {
            "error": str(e),
            "database_name": db_config.mongodb_database_name
        }})
        raise


async def close_database() -> None:
    """Close MongoDB connection"""
    global client

    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database


def get_client() -> AsyncIOMotorClient:
    """Get client instance"""
    if client is None:
        raise RuntimeError("Database client not initialized. Call init_database() first.")
    return client


# Health check function
async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        if client is None:
            return False
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.error("Database health check failed", extra={"extra_data": {"error": str(e)}})
        return False