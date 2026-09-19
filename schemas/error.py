from pydantic import BaseModel

class ErrorSchema(BaseModel):
    """ Define o formato padronizado de mensagens de erro da API """
    message: str