from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        print("🍃 Conectando ao MongoDB...")
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.MONGO_DB_NAME]
        print("✅ MongoDB Conectado.")

    def close(self):
        if self.client:
            print("🍃 Fechando conexão MongoDB...")
            self.client.close()

mongo_db = MongoDB()

async def get_database():
    return mongo_db.db