import json
from faststream.rabbit import RabbitBroker
from src.database.redis_client import get_redis
from src.database.mongo_client import get_database
from src.producer import broker 

@broker.subscriber("corridas_queue")
async def processar_corrida(msg: dict):
    
    print(f"📥 [Evento Recebido] Processando corrida: {msg.get('id_corrida')}")
    
    redis = await get_redis()
    db = await get_database()
    
    motorista_nome = msg['motorista']['nome']
    valor = msg['valor_corrida']
    id_corrida = msg.get('id_corrida') 

    try:
        
        chave_saldo = f"saldo:{motorista_nome.lower()}"
        novo_saldo = await redis.incrbyfloat(chave_saldo, valor)
        
        print(f"💰 [Redis] Saldo de {motorista_nome} atualizado para: {novo_saldo}")

       
        
        resultado = await db.corridas.update_one(
            {"_id": id_corrida},
            {
                "$set": {
                    "status": "processada",
                    "valor_final_processado": valor
                }
            }
        )
        
        if resultado.modified_count > 0:
            print(f"✅ [Mongo] Status da corrida {id_corrida} atualizado para 'processada'.")
        else:
            
            print(f"⚠️ [Mongo] Corrida {id_corrida} não encontrada para atualização.")

    except Exception as e:
        print(f"❌ Erro ao processar corrida {id_corrida}: {str(e)}")
       