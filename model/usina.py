from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from model.base import Base

class Usina(Base):
    __tablename__ = 'usina'

    id = Column(Integer, primary_key=True)
    nome = Column(String(140), unique=True, nullable=False)
    potencia_kwp = Column(Float, nullable=False)
    tensao_sistema_v = Column(Float, nullable=False)
    tipo_sistema = Column(String(50), nullable=False)
    cidade = Column(String(100), nullable=False)
    data_instalacao = Column(DateTime, default=datetime.now)
    data_insercao = Column(DateTime, default=datetime.now)

    # Relacionamento com as Baterias
    baterias = relationship("Bateria", back_populates="usina", cascade="all, delete-orphan")

    def __init__(self, nome: str, potencia_kwp: float, tensao_sistema_v: float, tipo_sistema: str, cidade: str, data_instalacao: datetime = None):
        self.nome = nome
        self.potencia_kwp = potencia_kwp
        self.tensao_sistema_v = tensao_sistema_v
        self.tipo_sistema = tipo_sistema
        self.cidade = cidade
        if data_instalacao:
            if isinstance(data_instalacao, str):
                self.data_instalacao = datetime.strptime(data_instalacao, "%Y-%m-%d")
            else:
                self.data_instalacao = data_instalacao