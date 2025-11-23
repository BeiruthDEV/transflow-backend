import json
from faststream.rabbit import RabbitBroker
from src.database.redis_client import get_redis
from src.database.mongo_client import get_database
from src.producer import broker  # Importamos o mesmo broker configurado

# Lógica do Consumidor (Worker)
# O decorador @broker.subscriber diz: "Fique ouvindo a fila 'corridas_queue'"
@broker.subscriber("corridas_queue")
async def processar_corrida(msg: dict):
    """
    Esta função é chamada AUTOMATICAMENTE sempre que chega uma nova mensagem no RabbitMQ.
    """
    print(f"📥 [Evento Recebido] Processando corrida: {msg.get('id_corrida')}")
    
    redis = await get_redis()
    db = await get_database()
    
    motorista_nome = msg['motorista']['nome']
    valor = msg['valor_corrida']
    id_corrida = msg.get('id_corrida') # ID gerado ou passado pelo cliente

    try:
        # ---------------------------------------------------------
        # 1. Atualização Atômica de Saldo no Redis (Requisito 2)
        # ---------------------------------------------------------
        # INCRBYFLOAT garante que se dois pagamentos entrarem ao mesmo tempo,
        # o saldo não buga. É atômico.
        chave_saldo = f"saldo:{motorista_nome.lower()}"
        novo_saldo = await redis.incrbyfloat(chave_saldo, valor)
        
        print(f"💰 [Redis] Saldo de {motorista_nome} atualizado para: {novo_saldo}")

        # ---------------------------------------------------------
        # 2. Persistência no MongoDB (Requisito 3)
        # ---------------------------------------------------------
        # Se a corrida já foi salva inicialmente como 'pendente', atualizamos para 'processada'
        # Caso contrário, inserimos o registro completo.
        
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
            # Fallback: Se por algum motivo o ID não existir, inserimos como nova
            # (Isso depende da regra de negócio, aqui assumimos atualização)
            print(f"⚠️ [Mongo] Corrida {id_corrida} não encontrada para atualização.")

    except Exception as e:
        print(f"❌ Erro ao processar corrida {id_corrida}: {str(e)}")
        # Aqui poderíamos implementar uma fila de 'Dead Letter' (DLQ) para tentar de novo depois