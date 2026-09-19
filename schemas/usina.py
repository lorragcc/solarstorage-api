from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.bateria import BateriaViewSchema

class UsinaSchema(BaseModel):
    """ Define a estrutura para cadastro de uma nova usina """
    nome: str = Field(..., example="Usina Solar Alpha")
    potencia_kwp: float = Field(..., example=15.5)
    tensao_sistema_v: float = Field(..., example=48.0)
    tipo_sistema: str = Field(..., example="Híbrido (Backup + Grid)")
    cidade: str = Field(..., example="Santa Isabel, SP")
    data_instalacao: str = Field(..., example="2026-08-22")

class UsinaBuscaPorIdSchema(BaseModel):
    """ Define a busca de usina por ID """
    id: int = Field(..., example=1, description="ID da usina")

class UsinaAtualizaSchema(BaseModel):
    """ Define os campos para atualização de uma usina """
    nome: str = Field(..., example="Usina Solar Alpha")
    potencia_kwp: float = Field(..., example=20.0)
    tensao_sistema_v: float = Field(..., example=48.0)
    tipo_sistema: str = Field(..., example="Híbrido (Backup + Grid)")
    cidade: str = Field(..., example="Santa Isabel, SP")
    data_instalacao: str = Field(..., example="2026-08-22")

class UsinaViewSchema(BaseModel):
    """ Define o formato de resposta detalhada de uma usina """
    id: int = 1
    nome: str = "Usina Solar Alpha"
    potencia_kwp: float = 15.5
    tensao_sistema_v: float = 48.0
    tipo_sistema: str = "Híbrido (Backup + Grid)"
    cidade: str = "Santa Isabel, SP"
    data_instalacao: str = "2026-08-22"
    total_kwh_armazenado: float = 7.68
    capacidade_util_total_kwh: float = 7.68
    baterias: List[BateriaViewSchema] = []

class ListaUsinasSchema(BaseModel):
    """ Define a resposta para a listagem completa de usinas """
    usinas: List[UsinaViewSchema]

def apresenta_usina(usina):
    """ 
    Retorna a representação formatada da usina e calcula a energia útil do banco BESS.
    Compatível com nomes de atributos antigos e novos (total_kwh_armazenado / capacidade_util_total_kwh).
    """
    baterias_formatadas = []
    total_kwh = 0.0

    if usina.baterias:
        for b in usina.baterias:
            # Recupera a tensão (usando a tensão do sistema da usina como fallback)
            tensao_v = float(b.tensao_nominal_v) if (b.tensao_nominal_v and float(b.tensao_nominal_v) > 0) else float(usina.tensao_sistema_v or 48.0)
            capacidade_ah = float(b.capacidade_ah) if (b.capacidade_ah and float(b.capacidade_ah) > 0) else 0.0
            quantidade = int(b.quantidade) if (b.quantidade and int(b.quantidade) > 0) else 1
            dod = float(b.dod_percentual) if (b.dod_percentual and float(b.dod_percentual) > 0) else 80.0

            # Normalização do fator de descarga DoD (se gravado como 80 ou 0.8)
            dod_fator = dod / 100.0 if dod > 1.0 else dod

            # Cálculo da energia útil armazenada em kWh: E = (V * Ah * Qtd / 1000) * (DoD / 100)
            kwh_util = (tensao_v * capacidade_ah * quantidade / 1000.0) * dod_fator
            total_kwh += kwh_util

            baterias_formatadas.append({
                "id": b.id,
                "tecnologia": b.tecnologia or "LiFePO4",
                "capacidade_ah": capacidade_ah,
                "tensao_nominal_v": tensao_v,
                "dod_percentual": dod,
                "quantidade": quantidade,
                "capacidade_util_kwh": round(kwh_util, 2),
                "energia_util_kwh": round(kwh_util, 2)
            })

    # Tratamento seguro da data de instalação
    data_inst = ""
    if usina.data_instalacao:
        if hasattr(usina.data_instalacao, 'strftime'):
            data_inst = usina.data_instalacao.strftime("%Y-%m-%d")
        else:
            data_inst = str(usina.data_instalacao)

    total_kwh_arredondado = round(total_kwh, 2)

    return {
        "id": usina.id,
        "nome": usina.nome,
        "potencia_kwp": usina.potencia_kwp,
        "tensao_sistema_v": usina.tensao_sistema_v,
        "tipo_sistema": usina.tipo_sistema,
        "cidade": usina.cidade,
        "data_instalacao": data_inst,
        "total_kwh_armazenado": total_kwh_arredondado,
        "capacidade_util_total_kwh": total_kwh_arredondado,
        "baterias": baterias_formatadas
    }