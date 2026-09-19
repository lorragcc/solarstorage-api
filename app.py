"""
Ponto de Entrada da API RESTful (Back-end Principal)
Projeto: SolarStorage — Gestão Fotovoltaica & Baterias
"""

from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from flask_cors import CORS

from controllers.usina_controller import registrar_rotas_usina
from controllers.bateria_controller import registrar_rotas_bateria

# Configuração Básica do Servidor e Documentação Swagger
info = Info(
    title="SolarStorage API",
    version="1.0.0",
    description="API RESTful para gestão cadastral e dimensionamento de usinas solares e baterias."
)
app = OpenAPI(__name__, info=info)
CORS(app)

doc_tag = Tag(name="Documentação", description="Redirecionamento para o Swagger UI")

@app.get('/', tags=[doc_tag])
def index():
    """Redireciona a raiz para o Swagger UI."""
    return redirect('/openapi/swagger')

# Registra os Módulos de Rotas (Controllers)
registrar_rotas_usina(app)
registrar_rotas_bateria(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)