from flask import Flask
from flasgger import Swagger
from rotas.auth import auth, bcrypt
from models.models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_muito_segura' # Protege as sessões e mensagens flash

# Inicializa as extensões
swagger = Swagger(app)
bcrypt.init_app(app)

# 1. Segurança: Abre a conexão antes de cada pedido
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

# 2. Segurança: Fecha a conexão após o pedido para libertar recursos
@app.after_request
def _db_close(response):
    if not db.is_closed():
        db.close()
    return response

# Regista o Blueprint das rotas
app.register_blueprint(auth)

if __name__ == '__main__':
    app.run(debug=True)