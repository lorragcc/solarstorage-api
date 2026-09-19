"""
Módulo de Rotas: Bateria
Projeto: SolarStorage — Gestão Fotovoltaica & Baterias
"""

from flask_openapi3 import Tag
from model import Session, Usina, Bateria
from schemas.usina import UsinaViewSchema, apresenta_usina
from schemas.bateria import (
    BateriaSchema, BateriaBuscaPorIdSchema, BateriaAtualizaSchema
)
from schemas.error import ErrorSchema

bateria_tag = Tag(name="Bateria", description="Operações de Vínculo de Módulos de Bateria")


def registrar_rotas_bateria(app):

    @app.post('/bateria', tags=[bateria_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "404": ErrorSchema})
    def adicionar_bateria(body: BateriaSchema):
        """Cadastra e vincula um novo banco de baterias a uma usina existente."""
        session = Session()
        usina = session.query(Usina).filter(Usina.id == body.usina_id).first()
        if not usina:
            return {"message": "Usina vinculada não foi encontrada."}, 404

        try:
            nova_bateria = Bateria(
                usina_id=body.usina_id,
                tecnologia=body.tecnologia,
                capacidade_ah=body.capacidade_ah,
                tensao_nominal_v=body.tensao_nominal_v,
                dod_percentual=body.dod_percentual,
                quantidade=body.quantidade
            )
            session.add(nova_bateria)
            session.commit()
            return apresenta_usina(usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao adicionar bateria: {str(e)}"}, 400

    @app.put('/bateria', tags=[bateria_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "404": ErrorSchema})
    def atualizar_bateria(query: BateriaBuscaPorIdSchema, body: BateriaAtualizaSchema):
        """Atualiza as especificações técnicas de um módulo de bateria."""
        session = Session()
        bateria = session.query(Bateria).filter(Bateria.id == query.id).first()
        if not bateria:
            return {"message": "Módulo de bateria não encontrado."}, 404

        try:
            bateria.tecnologia = body.tecnologia
            bateria.capacidade_ah = body.capacidade_ah
            bateria.tensao_nominal_v = body.tensao_nominal_v
            bateria.dod_percentual = body.dod_percentual
            bateria.quantidade = body.quantidade
            session.commit()

            usina = session.query(Usina).filter(Usina.id == bateria.usina_id).first()
            return apresenta_usina(usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao atualizar bateria: {str(e)}"}, 400

    @app.delete('/bateria', tags=[bateria_tag], responses={"200": ErrorSchema, "404": ErrorSchema})
    def remover_bateria(query: BateriaBuscaPorIdSchema):
        """Remove um módulo de bateria individual do sistema."""
        session = Session()
        bateria = session.query(Bateria).filter(Bateria.id == query.id).first()
        if not bateria:
            return {"message": "Módulo de bateria não encontrado."}, 404

        try:
            session.delete(bateria)
            session.commit()
            return {"message": "Módulo de bateria removido com sucesso."}, 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao remover bateria: {str(e)}"}, 400