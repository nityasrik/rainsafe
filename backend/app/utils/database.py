"""
Database connection and utilities
"""

import os
import motor.motor_asyncio
from config.settings import MONGO_URI, DATABASE_NAME


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client = None
        self.database = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            self.database = self.client[DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.database:
            raise RuntimeError("Database not connected")
        return self.database[collection_name]


# Global database instance
db = Database()
