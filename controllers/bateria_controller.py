"""
Módulo de Rotas: Bateria
Projeto: SolarStorage — Gestão Fotovoltaica & Baterias
"""

from flask_openapi3 import OpenAPI, Tag
from model import Session, Usina, Bateria
from schemas.usina import UsinaViewSchema, apresenta_usina
from schemas.bateria import (
    BateriaSchema, BateriaBuscaPorIdSchema, BateriaAtualizaSchema
)
from schemas.error import ErrorSchema

# Tag com instrução explícita de fluxo para o Swagger UI
bateria_tag = Tag(
    name="Bateria", 
    description="Operações no Banco BESS. 💡 Para consultar os IDs existentes para atualização/remoção, execute primeiro a rota GET /usinas."
)


def registrar_rotas_bateria(app: OpenAPI):
    """Registra todos os endpoints de baterias no aplicativo Flask-OpenAPI3."""

    @app.post('/bateria', tags=[bateria_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "404": ErrorSchema})
    def adicionar_bateria(body: BateriaSchema):
        """
        Cadastra e vincula um novo banco de baterias a uma usina existente.
        
        📌 Dica de Teste: Certifique-se de informar um `usina_id` válido. Os IDs das usinas podem ser consultados no endpoint GET /usinas.
        """
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
        """
        Atualiza as especificações técnicas de um módulo de bateria.
        
        📌 Dica de Teste: Para obter o `id` da bateria a ser atualizada, consulte previamente a rota GET /usinas ou GET /usina?id={id}.
        """
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
        """
        Remove um módulo de bateria individual do sistema.
        
        📌 Dica de Teste: Para obter o `id` da bateria a ser removida, consulte previamente a rota GET /usinas ou GET /usina?id={id}.
        """
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
