from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao, Professor, Aluno

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/login', methods=['POST'])
def login():
  
    dados = request.get_json()
    login = dados.get('login')
    senha = dados.get('senha')
    
    # Procura em todas as tabelas por email ou CPF [cite: 8, 9]
    user = (Instituicao.get_or_none(Instituicao.email == login) or 
        Professor.get_or_none((Professor.email == login) | (Professor.CPF == login)) or 
        Aluno.get_or_none((Aluno.email == login) | (Aluno.CPF == login)))
    
    if user and bcrypt.check_password_hash(user.senha, senha):
        return jsonify({"status": "sucesso", "message": "Login realizado!"}), 200
    
    return jsonify({"status": "erro", "message": "Credenciais inválidas"}), 401
