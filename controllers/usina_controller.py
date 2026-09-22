"""
Módulo de Rotas: Usina
Projeto: SolarStorage — Gestão Fotovoltaica & Baterias
"""

from flask_openapi3 import OpenAPI, Tag
from model import Session, Usina
from schemas.usina import (
    UsinaSchema, 
    UsinaBuscaPorIdSchema, 
    UsinaAtualizaSchema, 
    UsinaViewSchema, 
    ListaUsinasSchema, 
    apresenta_usina
)
from schemas.error import ErrorSchema
from datetime import datetime, date

# Tag com instrução explícita de fluxo para o Swagger UI
usina_tag = Tag(
    name="Usina", 
    description="Operações nas Usinas Fotovoltaicas. 💡 Para atualizar ou remover usinas, consulte previamente a lista de IDs existentes executando a rota GET /usinas."
)


def registrar_rotas_usina(app: OpenAPI):
    """Registra todos os endpoints de usinas no aplicativo Flask-OpenAPI3."""

    @app.get('/usinas', tags=[usina_tag], responses={"200": ListaUsinasSchema, "400": ErrorSchema})
    def obter_usinas():
        """
        Retorna a listagem completa de usinas fotovoltaicas e seus respectivos bancos de baterias (BESS).
        
        📌 Dica de Teste: Utilize esta rota em primeiro lugar para obter os IDs de usinas e baterias necessários para os testes de atualização (PUT) e remoção (DELETE).
        """
        session = Session()
        try:
            usinas = session.query(Usina).all()
            result = [apresenta_usina(u) for u in usinas]
            return {"usinas": result}, 200
        except Exception as e:
            return {"message": f"Erro ao buscar usinas: {str(e)}"}, 400

    @app.get('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "404": ErrorSchema})
    def obter_usina_por_id(query: UsinaBuscaPorIdSchema):
        """
        Busca os dados detalhados de uma única usina fotovoltaica pelo seu ID.
        
        📌 Dica de Teste: Caso não saiba qual `id` informar, execute primeiro a rota GET /usinas.
        """
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada."}, 404

        return apresenta_usina(usina), 200

    @app.post('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "409": ErrorSchema})
    def adicionar_usina(body: UsinaSchema):
        """
        Cadastra uma nova usina fotovoltaica no banco de dados.
        
        📌 Dica de Teste: O nome da usina deve ser único. Nomes duplicados retornarão status 409 Conflict.
        """
        session = Session()

        # Validação de Unicidade
        usina_existente = session.query(Usina).filter(Usina.nome == body.nome).first()
        if usina_existente:
            return {"message": f"Já existe uma usina cadastrada com o nome '{body.nome}'."}, 409

        try:
            nova_usina = Usina(
                nome=body.nome,
                potencia_kwp=body.potencia_kwp,
                tensao_sistema_v=body.tensao_sistema_v,
                tipo_sistema=body.tipo_sistema,
                cidade=body.cidade,
                data_instalacao=body.data_instalacao
            )
            session.add(nova_usina)
            session.commit()
            return apresenta_usina(nova_usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao cadastrar usina: {str(e)}"}, 400

    @app.put('/usina', tags=[usina_tag], responses={"200": UsinaViewSchema, "400": ErrorSchema, "404": ErrorSchema, "409": ErrorSchema})
    def atualizar_usina(query: UsinaBuscaPorIdSchema, body: UsinaAtualizaSchema):
        """
        Atualiza as especificações técnicas ou dados cadastrais de uma usina existente.
        
        📌 Dica de Teste: Para obter o `id` da usina a ser atualizada, consulte previamente a rota GET /usinas.
        """
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada para atualização."}, 404

        # Verifica duplicidade de nome se o nome for alterado
        if body.nome != usina.nome:
            nome_duplicado = session.query(Usina).filter(Usina.nome == body.nome, Usina.id != query.id).first()
            if nome_duplicado:
                return {"message": f"O nome '{body.nome}' já está em uso por outra usina."}, 409

        try:
            usina.nome = body.nome
            usina.potencia_kwp = body.potencia_kwp
            usina.tensao_sistema_v = body.tensao_sistema_v
            usina.tipo_sistema = body.tipo_sistema
            usina.cidade = body.cidade
            
            # Conversão pontual para o SQLite aceitar a data
            if isinstance(body.data_instalacao, str):
                usina.data_instalacao = datetime.strptime(body.data_instalacao, "%Y-%m-%d")
            else:
                usina.data_instalacao = body.data_instalacao
            
            session.commit()
            return apresenta_usina(usina), 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao atualizar usina: {str(e)}"}, 400

    @app.delete('/usina', tags=[usina_tag], responses={"200": ErrorSchema, "404": ErrorSchema})
    def remover_usina(query: UsinaBuscaPorIdSchema):
        """
        Remove uma usina do sistema e expurga em cascata todos os seus módulos de bateria vinculados.
        
        📌 Dica de Teste: Para obter o `id` da usina a ser removida, consulte previamente a rota GET /usinas.
        """
        session = Session()
        usina = session.query(Usina).filter(Usina.id == query.id).first()
        if not usina:
            return {"message": "Usina não encontrada para remoção."}, 404

        try:
            session.delete(usina)
            session.commit()
            return {"message": "Usina e seus módulos BESS foram removidos com sucesso."}, 200
        except Exception as e:
            session.rollback()
            return {"message": f"Erro ao remover usina: {str(e)}"}, 400
