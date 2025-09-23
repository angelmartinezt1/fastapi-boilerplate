import asyncio
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from pymongo.database import Database
from app.config.settings import db_config
from app.utils.logger import logger
from typing import Optional

# Global database instances
client: Optional[MongoClient] = None
database: Optional[Database] = None
executor: Optional[ThreadPoolExecutor] = None


def init_database() -> None:
    """Initialize MongoDB connection (sync)"""
    global client, database, executor

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
        client = MongoClient(
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

        # Initialize thread pool executor for async operations
        executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="pymongo")

        # Test connection
        client.admin.command('ping')

        logger.info("MongoDB connection established successfully", extra={"extra_data": {
            "database_name": db_config.mongodb_database_name
        }})

    except Exception as e:
        logger.error("Failed to initialize MongoDB connection", extra={"extra_data": {
            "error": str(e),
            "database_name": db_config.mongodb_database_name
        }})
        raise


def close_database() -> None:
    """Close MongoDB connection"""
    global client, executor

    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None
        logger.info("MongoDB connection closed")

    if executor:
        logger.info("Shutting down thread pool executor")
        executor.shutdown(wait=True)
        executor = None
        logger.info("Thread pool executor shut down")


def get_database() -> Database:
    """Get database instance"""
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database


def get_client() -> MongoClient:
    """Get client instance"""
    if client is None:
        raise RuntimeError("Database client not initialized. Call init_database() first.")
    return client


def get_executor() -> ThreadPoolExecutor:
    """Get thread pool executor instance"""
    if executor is None:
        raise RuntimeError("Thread pool executor not initialized. Call init_database() first.")
    return executor


async def run_in_executor(func, *args):
    """Run sync function in thread pool executor"""
    loop = asyncio.get_event_loop()
    executor_instance = get_executor()
    return await loop.run_in_executor(executor_instance, func, *args)


# Health check function
async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        if client is None:
            return False

        def _ping():
            return client.admin.command('ping')

        await run_in_executor(_ping)
        return True
    except Exception as e:
        logger.error("Database health check failed", extra={"extra_data": {"error": str(e)}})
        return False