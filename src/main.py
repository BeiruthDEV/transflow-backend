from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List

# Importações dos nossos módulos
from src.database.mongo_client import mongo_db, get_database
from src.database.redis_client import redis_db, get_redis
from src.producer import broker, publicar_corrida
from src.models.corrida_model import CorridaCreate, CorridaResponse

# IMPORTANTE: Importamos o consumer para registrar os subscribers (listeners) do RabbitMQ
# Sem isso, o worker não saberia que precisa processar as mensagens.
import src.consumer 

# ---------------------------------------------------------
# 1. Gerenciamento do Ciclo de Vida (Lifespan)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("🚀 Inicializando conexões...")
    mongo_db.connect()
    redis_db.connect()
    await broker.start() # Conecta no RabbitMQ e inicia os consumers
    
    yield # A aplicação roda aqui
    
    # --- Shutdown ---
    print("🛑 Encerrando conexões...")
    await broker.close()
    await redis_db.close()
    mongo_db.close()

# Inicialização do App
app = FastAPI(
    title="TransFlow API",
    description="Sistema de gestão de corridas com processamento assíncrono.",
    version="1.0.0",
    lifespan=lifespan
)

# ---------------------------------------------------------
# 2. Endpoints (Rotas)
# ---------------------------------------------------------

@app.post("/corridas", response_model=CorridaResponse, status_code=201)
async def cadastrar_corrida(corrida: CorridaCreate):
    """
    Cadastra uma nova corrida, salva no Mongo como 'pendente' 
    e envia para processamento assíncrono (RabbitMQ).
    """
    db = await get_database()
    
    # 1. Converte o modelo Pydantic para dicionário
    corrida_dict = corrida.model_dump()
    
    # 2. Define estado inicial
    corrida_dict["status"] = "pendente"
    
    # 3. Salva no Mongo (Persistência inicial)
    nova_corrida = await db.corridas.insert_one(corrida_dict)
    
    # 4. Adiciona o ID gerado ao dicionário para enviar na mensagem
    corrida_dict["id_corrida"] = str(nova_corrida.inserted_id)
    
    # 5. Publica evento no RabbitMQ (Fire and Forget)
    await publicar_corrida(corrida_dict)
    
    # 6. Retorna resposta rápida ao cliente
    return {**corrida_dict, "_id": str(nova_corrida.inserted_id)}


@app.get("/corridas", response_model=List[CorridaResponse])
async def listar_corridas():
    """
    Lista todas as corridas registradas no banco.
    """
    db = await get_database()
    corridas = await db.corridas.find().to_list(length=100)
    return corridas


@app.get("/corridas/{forma_pagamento}", response_model=List[CorridaResponse])
async def filtrar_corridas(forma_pagamento: str):
    """
    Filtra corridas por forma de pagamento (ex: DigitalCoin, Pix, Credito).
    """
    db = await get_database()
    corridas = await db.corridas.find({"forma_pagamento": forma_pagamento}).to_list(length=100)
    return corridas


@app.get("/saldo/{motorista}")
async def consultar_saldo(motorista: str):
    """
    Consulta o saldo acumulado do motorista no Redis (Processado pelos Workers).
    """
    redis = await get_redis()
    
    chave_saldo = f"saldo:{motorista.lower()}"
    saldo = await redis.get(chave_saldo)
    
    if saldo is None:
        return {"motorista": motorista, "saldo": 0.0}
    
    return {"motorista": motorista, "saldo": float(saldo)}