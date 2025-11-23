from fastapi import FastAPI, HTTPException # adicionei HTTPException caso precise no futuro, mas o foco é o Redirect
from fastapi.responses import RedirectResponse # <--- IMPORTANTE: Adicione isso
from contextlib import asynccontextmanager
from typing import List
import uuid

from src.config import settings
from src.database.mongo_client import mongo_db, get_database
from src.database.redis_client import redis_db, get_redis
from src.producer import broker, publicar_corrida
from src.models.corrida_model import CorridaCreate, CorridaResponse
import src.consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Iniciando {settings.APP_NAME}...")
    mongo_db.connect()
    redis_db.connect()
    await broker.start()
    
    yield
    
    print("🛑 Encerrando conexões...")
    await broker.close()
    await redis_db.close()
    mongo_db.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# --- NOVO BLOCO: Redireciona a raiz para /docs ---
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
# -------------------------------------------------

@app.post("/corridas", response_model=CorridaResponse, status_code=201)
async def criar_corrida(corrida: CorridaCreate):
    db = await get_database()
    
    corrida_dict = corrida.model_dump()
    corrida_dict["status"] = "pendente"
    corrida_dict["id_corrida"] = str(uuid.uuid4())[:8]

    result = await db.corridas.insert_one(corrida_dict)
    
    mongo_id = str(result.inserted_id)
    corrida_dict["_id"] = mongo_id

    await publicar_corrida(corrida_dict)

    return corrida_dict

@app.get("/corridas", response_model=List[CorridaResponse])
async def listar_corridas():
    db = await get_database()
    corridas = await db.corridas.find().to_list(100)
    return corridas

@app.get("/corridas/{forma_pagamento}", response_model=List[CorridaResponse])
async def filtrar_corridas(forma_pagamento: str):
    db = await get_database()
    corridas = await db.corridas.find({"forma_pagamento": forma_pagamento}).to_list(100)
    return corridas

@app.get("/saldo/{motorista}")
async def consultar_saldo(motorista: str):
    redis = await get_redis()
    chave = f"saldo:{motorista.lower()}"
    
    saldo = await redis.get(chave)
    if not saldo:
        saldo = 0.0
        
    return {
        "motorista": motorista,
        "saldo": float(saldo)
    }