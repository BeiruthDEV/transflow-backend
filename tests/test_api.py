import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from src.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
async def test_criar_corrida_sucesso():
   
    
    payload = {
        "passageiro": {"nome": "Teste", "telefone": "123"},
        "motorista": {"nome": "Motorista Teste", "nota": 5.0},
        "origem": "A",
        "destino": "B",
        "valor_corrida": 20.0,
        "forma_pagamento": "Pix"
    }

    with patch("src.main.publicar_corrida", new_callable=AsyncMock) as mock_publicar:
        
        with patch("src.main.get_database") as mock_get_db:
            mock_db_instance = AsyncMock()
            mock_collection = AsyncMock()
            
            mock_insert_result = AsyncMock()
            mock_insert_result.inserted_id = "507f1f77bcf86cd799439011"
            
            mock_collection.insert_one.return_value = mock_insert_result
            mock_db_instance.corridas = mock_collection
            mock_get_db.return_value = mock_db_instance

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post("/corridas", json=payload)

            assert response.status_code == 201
            data = response.json()
            
            assert data["_id"] == "507f1f77bcf86cd799439011"
            assert data["status"] == "pendente"
            
            mock_publicar.assert_called_once()
            print("\n✅ Teste de Criação de Corrida: SUCESSO")

@pytest.mark.asyncio
async def test_consultar_saldo_redis():
    
    motorista = "Joao"
    
    with patch("src.main.get_redis") as mock_get_redis:
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = "50.5"
        mock_get_redis.return_value = mock_redis_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get(f"/saldo/{motorista}")

        assert response.status_code == 200
        assert response.json() == {"motorista": motorista, "saldo": 50.5}
        print("\n✅ Teste de Consulta de Saldo: SUCESSO")