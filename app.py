from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from rotas.auth import auth, bcrypt
from rotas.avaliacao import avaliacao 
from rotas.aluno import aluno
from rotas.questao import questao_bp    
from rotas.professor import professor
from rotas.instituicao import instituicao
from models.models import db, Instituicao, Aluno, Professor, Avaliacao, Questao, QuestaoAvaliacao, RespostaAvaliacao, RespostaQuestao


app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_muito_segura' # Protege as sessões e mensagens flash

# Lista de URLs permitidas (ajuste as portas do localhost se necessário)
allowed_origins = [
    "https://sistemaeva-api.onrender.com", # Servidor Backend Render
    "https://sistemaeva.onrender.com/" # Servidor Frontend Render
]

CORS(app, resources={r"/*": {"origins": allowed_origins}})


# Inicializa as extensões
swagger = Swagger(app)
bcrypt.init_app(app)

# 1. Segurança: Abre a conexão antes de cada pedido
@app.before_request
def _db_connect():
    if request.method == 'OPTIONS':
        return response
    if db.is_closed():
        db.connect()

# 2. Segurança: Fecha a conexão após o pedido para libertar recursos
@app.after_request
def _db_close(response):
    if request.method == 'OPTIONS':
        return response
    if not db.is_closed():
        db.close()
    return response

# Regista o Blueprint das rotas
app.register_blueprint(auth)
app.register_blueprint(avaliacao)
app.register_blueprint(aluno)
app.register_blueprint(professor)
app.register_blueprint(instituicao)
app.register_blueprint(questao_bp)

# Inicialização do banco de dados (executa tanto no Gunicorn quanto localmente)
try:
    db.connect()
    db.create_tables([
        Instituicao, Professor, Aluno, 
        Avaliacao, Questao, QuestaoAvaliacao, 
        RespostaAvaliacao, RespostaQuestao
    ], safe=True)
    print("Banco de dados e tabelas verificados/criados com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar o banco: {e}")
finally:
    db.close()


if __name__ == '__main__':
    app.run(debug=True)
