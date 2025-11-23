from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Passageiro(BaseModel):
    nome: str
    telefone: str

class Motorista(BaseModel):
    nome: str
    nota: float

class CorridaBase(BaseModel):
    passageiro: Passageiro
    motorista: Motorista
    origem: str
    destino: str
    valor_corrida: float
    forma_pagamento: str

class CorridaCreate(CorridaBase):
    pass

class CorridaResponse(CorridaBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    status: str = "pendente"
    id_corrida: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "6512a...",
                "status": "processada",
                "motorista": {"nome": "Carla", "nota": 4.8},
                "valor_corrida": 35.50,
                "forma_pagamento": "DigitalCoin"
            }
        }