from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List


from src.database.mongo_client import mongo_db, get_database
from src.database.redis_client import redis_db, get_redis
from src.producer import broker, publicar_corrida
from src.models.corrida_model import CorridaCreate, CorridaResponse


import src.consumer 


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("🚀 Inicializando conexões...")
    mongo_db.connect()
    redis_db.connect()
    await broker.start() 
    yield 
    
    
    print("🛑 Encerrando conexões...")
    await broker.close()
    await redis_db.close()
    mongo_db.close()


app = FastAPI(
    title="TransFlow API",
    description="Sistema de gestão de corridas com processamento assíncrono.",
    version="1.0.0",
    lifespan=lifespan
)



@app.post("/corridas", response_model=CorridaResponse, status_code=201)
async def cadastrar_corrida(corrida: CorridaCreate):
    
    db = await get_database()
    
    
    corrida_dict = corrida.model_dump()
    
    corrida_dict["status"] = "pendente"
    
    nova_corrida = await db.corridas.insert_one(corrida_dict)
    
    corrida_dict["id_corrida"] = str(nova_corrida.inserted_id)
    
    await publicar_corrida(corrida_dict)
    
    return {**corrida_dict, "_id": str(nova_corrida.inserted_id)}


@app.get("/corridas", response_model=List[CorridaResponse])
async def listar_corridas():
    
    db = await get_database()
    corridas = await db.corridas.find().to_list(length=100)
    return corridas


@app.get("/corridas/{forma_pagamento}", response_model=List[CorridaResponse])
async def filtrar_corridas(forma_pagamento: str):
    
    db = await get_database()
    corridas = await db.corridas.find({"forma_pagamento": forma_pagamento}).to_list(length=100)
    return corridas


@app.get("/saldo/{motorista}")
async def consultar_saldo(motorista: str):
    
    redis = await get_redis()
    
    chave_saldo = f"saldo:{motorista.lower()}"
    saldo = await redis.get(chave_saldo)
    
    if saldo is None:
        return {"motorista": motorista, "saldo": 0.0}
    
    return {"motorista": motorista, "saldo": float(saldo)}