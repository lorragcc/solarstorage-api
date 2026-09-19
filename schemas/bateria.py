from pydantic import BaseModel, Field

class BateriaSchema(BaseModel):
    """ Define como uma nova bateria associada a uma usina deve ser representada """
    usina_id: int = Field(..., example=1, description="ID da usina vinculada")
    tecnologia: str = Field(..., example="LiFePO4")
    capacidade_ah: float = Field(..., example=100.0)
    tensao_nominal_v: float = Field(..., example=48.0)
    dod_percentual: float = Field(..., example=80.0)
    quantidade: int = Field(1, example=2)

class BateriaBuscaPorIdSchema(BaseModel):
    """ Define a busca/deleção de uma bateria via ID """
    id: int = Field(..., example=1, description="ID da bateria")

class BateriaAtualizaSchema(BaseModel):
    """ Define os campos para atualização das especificações da bateria """
    tecnologia: str = Field(..., example="LiFePO4")
    capacidade_ah: float = Field(..., example=100.0)
    tensao_nominal_v: float = Field(..., example=48.0)
    dod_percentual: float = Field(..., example=80.0)
    quantidade: int = Field(..., example=2)

class BateriaViewSchema(BaseModel):
    """ Define como os dados de uma bateria individual serão estruturados na resposta """
    id: int = 1
    tecnologia: str = "LiFePO4"
    capacidade_ah: float = 100.0
    tensao_nominal_v: float = 48.0
    dod_percentual: float = 80.0
    quantidade: int = 2
    capacidade_util_kwh: float = 7.68