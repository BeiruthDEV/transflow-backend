import redis.asyncio as redis
from src.config import settings

class RedisClient:
    client: redis.Redis = None

    def connect(self):
        print("🔥 Conectando ao Redis...")
       
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True 
        )
        print("✅ Redis Conectado.")

    async def close(self):
        if self.client:
            print("🔥 Fechando conexão Redis...")
            await self.client.close()

redis_db = RedisClient()

async def get_redis():
    return redis_db.client