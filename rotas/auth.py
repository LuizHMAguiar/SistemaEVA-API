from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao, Professor, Aluno

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/login', methods=['POST'])
def login():
    """
    Realiza o login de utilizadores
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "user@email.com"
            senha:
              type: string
              example: "minhaSenha123"
    responses:
      200:
        description: Login realizado com sucesso
      401:
        description: E-mail ou senha incorretos
    """
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

@auth.route('/cadastro/instituicao', methods=['POST'])
def cadastro_instituicao():
    """
    Cadastra uma nova Instituição
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cnpj:
              type: string
              example: "11222333444455"
            nome:
              type: string
              example: "Escola ABC"
            email:
              type: string
              example: "escola@email.com"
            senha:
              type: string
              example: "minhaSenha123"
    responses:
      201:
        description: Instituição criada
    """
    dados = request.get_json()
    
    # Verifica se a instituição já existe
    if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('cnpj')):
      return jsonify({"error": "CNPJ já cadastrado"}), 409
    
    if Instituicao.get_or_none(Instituicao.email == dados.get('email')):
      return jsonify({"error": "E-mail já cadastrado"}), 409
    
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
      # Colunas: CNPJ, nome, email, senha [cite: 9]
      Instituicao.create(
        CNPJ=dados.get('cnpj'),
        nome=dados.get('nome'),
        email=dados.get('email'),
        senha=senha_hash
      )
      return jsonify({"message": "Instituição cadastrada com sucesso!"}), 201
    except IntegrityError:
      return jsonify({"error": "Erro de integridade dos dados"}), 400
    except Exception as e:
      return jsonify({"error": "Erro ao cadastrar instituição", "details": str(e)}), 500

@auth.route('/cadastro/professor', methods=['POST'])
def cadastro_professor():
    """
    Cadastra um novo Professor
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cpf:
              type: string
              example: "12345678900"
            cnpj_instituicao:
              type: string
              example: "11222333444455"
            nome_completo:
              type: string
              example: "João Silva"
            email:
              type: string
              example: "joao@email.com"
            senha:
              type: string
              example: "minhaSenha123"
    responses:
      201:
        description: Professor criado
    """
    dados = request.get_json()

    if Professor.get_or_none(Professor.CPF == dados.get('cpf')):
      return jsonify({"error": "CPF já cadastrado"}), 409
    
    if Professor.get_or_none(Professor.email == dados.get('email')):
      return jsonify({"error": "E-mail já cadastrado"}), 409

    # Verificar se a chave estrangeira corresponde a uma PK existente na outra tabela. 
    # TODO: Fazer isso para todas
    if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('cnpj_instituicao')) == None:
      return jsonify({"error": "Instituição não cadastrada"}), 400


    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
        # Colunas: CPF, CNPJ_instituicao_id, nome_completo, email, senha [cite: 8]
        Professor.create(
            CPF=dados.get('cpf'),
            CNPJ_instituicao=dados.get('cnpj_instituicao'),
            nome_completo=dados.get('nome_completo'),
            email=dados.get('email'),
            senha=senha_hash
        )
        return jsonify({"message": "Professor cadastrado com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "Erro de integridade"}), 400

@auth.route('/cadastro/aluno', methods=['POST'])
def cadastro_aluno():
    """
    Cadastra um novo Aluno
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cpf:
              type: string
              example: "12345678900"
            cnpj_instituicao:
              type: string
              example: "11222333444455"
            nome_completo:
              type: string
              example: "João da Silva"
            email:
              type: string
              example: "joao@email.com"
            senha:
              type: string
              example: "minhaSenha123"
            curso:
              type: string
              example: "Engenharia"
            turma:
              type: string
              example: "A1"
    responses:
      201:
        description: Aluno criado
    """

    dados = request.get_json()
    if dados is None:
      return jsonify({"error": "Formato inválido do body da requisição JSON"}), 400
    
    if Aluno.get_or_none(Aluno.CPF == dados.get('cpf')):
      return jsonify({"error": "CPF já cadastrado"}), 409
    
    if Aluno.get_or_none(Aluno.email == dados.get('email')):
      return jsonify({"error": "E-mail já cadastrado"}), 409
    
    if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('cnpj_instituicao')) == None:
      return jsonify({"error": "Instituição não cadastrada"}), 400
    
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    
    try:
        # Colunas: CPF, CNPJ_instituicao_id, nome_completo, email, senha, curso, turma [cite: 9]
        Aluno.create(
            CPF=dados.get('cpf'),
            CNPJ_instituicao=dados.get('cnpj_instituicao'),
            nome_completo=dados.get('nome_completo'),
            email=dados.get('email'),
            senha=senha_hash,
            curso=dados.get('curso'),
            turma=dados.get('turma')
        )
        return jsonify({"message": "Aluno cadastrado com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "Erro de integridade"}), 400