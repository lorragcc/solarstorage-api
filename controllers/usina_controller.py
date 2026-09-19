"""
Módulo de Rotas: Usina Fotovoltaica
Projeto: SolarStorage — Gestão Fotovoltaica & Baterias
"""

from datetime import datetime
from flask_openapi3 import Tag, OpenAPI
from model import Session, Usina
from schemas.usina import (
    UsinaSchema, UsinaBuscaPorIdSchema, UsinaAtualizaSchema,
    UsinaViewSchema, ListaUsinasSchema, apresenta_usina
)
from schemas.error import ErrorSchema

usina_tag = Tag(name="Usina", description="Operações de CRUD de Usinas Fotovoltaicas")


def converter_para_datetime(data_str):
    """
    Converte uma string de data (YYYY-MM-DD ou ISO) para um objeto datetime.date do Python.
    Resolve o erro de conversão nativa do SQLAlchemy com SQLite.
    """
    if not data_str:
        return datetime.today().date()
    
    if isinstance(data_str, datetime):
        return data_str.date()
    
    if hasattr(data_str, 'year'):
        return data_str

    try:
        # Tenta o formato ISO padrão YYYY-MM-DD
        return datetime.strptime(str(data_str).split('T')[0], "%Y-%m-%d").date()
    except ValueError:
        try:
            # Tenta o formato brasileiro DD/MM/YYYY
            return datetime.strptime(str(data_str), "%d/%m/%Y").date()
        except ValueError:
            return datetime.today().date()


def registrar_rotas_usina(app: OpenAPI):

    @app.post('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "409": ErrorSchema})
    def cadastrar_usina(body: UsinaSchema):
        """Cadastra uma nova usina fotovoltaica no banco de dados."""
        session = Session()
        usina_existente = session.query(Usina).filter(Usina.nome == body.nome).first()
        if usina_existente:
            return {"message": "Já existe uma usina cadastrada com este nome."}, 409

        try:
            nova_usina = Usina(
                nome=body.nome,
                potencia_kwp=body.potencia_kwp,
                tensao_sistema_v=body.tensao_sistema_v,
                tipo_sistema=body.tipo_sistema,
                cidade=body.cidade,
                data_instalacao=converter_para_datetime(body.data_instalacao)
            )
            session.add(nova_usina)
            session.commit()
            return apresenta_usina(nova_usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro interno ao cadastrar usina: {str(e)}"}, 400

    @app.get('/usinas', tags=[usina_tag], responses={"200": ListaUsinasSchema})
    def listar_usinas():
        """Lista todas as usinas cadastradas juntamente com seus bancos de baterias."""
        session = Session()
        usinas = session.query(Usina).all()
        return {"usinas": [apresenta_usina(u) for u in usinas]}, 200

    @app.get('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "404": ErrorSchema})
    def buscar_usina(query: UsinaBuscaPorIdSchema):
        """Busca uma usina específica pelo seu ID."""
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada."}, 404
        return apresenta_usina(usina), 200

    @app.put('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "404": ErrorSchema, "409": ErrorSchema})
    def atualizar_usina(query: UsinaBuscaPorIdSchema, body: UsinaAtualizaSchema):
        """Atualiza as especificações técnicas ou cadastrais de uma usina existente."""
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada."}, 404

        conflito_nome = session.query(Usina).filter(Usina.nome == body.nome, Usina.id != query.id).first()
        if conflito_nome:
            return {"message": "Outra usina já utiliza este nome no sistema."}, 409

        try:
            usina.nome = body.nome
            usina.potencia_kwp = body.potencia_kwp
            usina.tensao_sistema_v = body.tensao_sistema_v
            usina.tipo_sistema = body.tipo_sistema
            usina.cidade = body.cidade
            usina.data_instalacao = converter_para_datetime(body.data_instalacao)
            
            session.commit()
            return apresenta_usina(usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao atualizar usina: {str(e)}"}, 400

    @app.delete('/usina', tags=[usina_tag], responses={"200": ErrorSchema, "404": ErrorSchema})
    def deletar_usina(query: UsinaBuscaPorIdSchema):
        """Remove uma usina do sistema (Aplica exclusão em cascata nas baterias)."""
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada."}, 404

        try:
            session.delete(usina)
            session.commit()
            return {"message": "Usina e seus módulos de bateria foram removidos."}, 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao excluir usina: {str(e)}"}, 400