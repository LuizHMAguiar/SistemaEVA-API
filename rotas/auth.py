from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao, Professor, Aluno
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    login = dados.get('login')
    senha = dados.get('senha')

    # Verifica em cada tabela separadamente para determinar o tipo de usuário
    instituicao = Instituicao.get_or_none(Instituicao.email == login)
    professor = Professor.get_or_none((Professor.email == login) | (Professor.CPF == login))
    aluno = Aluno.get_or_none((Aluno.email == login) | (Aluno.CPF == login))

    user = instituicao or professor or aluno

    if user and bcrypt.check_password_hash(user.senha, senha):
        if instituicao:
            identity = instituicao.CNPJ
            usuario = {
                'nome': instituicao.nome,
                'email': instituicao.email,
                'cnpj': instituicao.CNPJ,
                'tipo': 'instituicao'
            }
        elif professor:
            identity = professor.CPF
            usuario = {
                'nome': professor.nome_completo,
                'email': professor.email,
                'cpf': professor.CPF,
                'instituicao': professor.CNPJ_instituicao_id,
                'tipo': 'professor'
            }
        else:
            identity = aluno.CPF
            usuario = {
                'nome': aluno.nome_completo,
                'email': aluno.email,
                'cpf': aluno.CPF,
                'instituicao': aluno.CNPJ_instituicao_id,
                'tipo': 'aluno'
            }

        # Gera o token
        token = create_access_token(identity=identity)

        return jsonify({
            'status': 'sucesso',
            'message': 'Login realizado!',
            'usuario': usuario,
            'token': token
        }), 200

    return jsonify({'status': 'erro', 'message': 'Credenciais inválidas'}), 401
