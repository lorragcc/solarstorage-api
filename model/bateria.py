from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base

class Bateria(Base):
    __tablename__ = 'bateria'

    id = Column(Integer, primary_key=True)
    usina_id = Column(Integer, ForeignKey('usina.id'), nullable=False)
    tecnologia = Column(String(50), nullable=False)
    capacidade_ah = Column(Float, nullable=False)
    tensao_nominal_v = Column(Float, nullable=False)
    dod_percentual = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)

    # Relacionamento com a Usina
    usina = relationship("Usina", back_populates="baterias")

    def __init__(self, usina_id: int, tecnologia: str, capacidade_ah: float, tensao_nominal_v: float, dod_percentual: float, quantidade: int = 1):
        self.usina_id = usina_id
        self.tecnologia = tecnologia
        self.capacidade_ah = capacidade_ah
        self.tensao_nominal_v = tensao_nominal_v
        self.dod_percentual = dod_percentual
        self.quantidade = quantidade