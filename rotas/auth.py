from flask import Blueprint, request, jsonify, redirect, url_for, flash
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
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: senha
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Login realizado com sucesso
      401:
        description: E-mail ou senha incorretos
    """
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    # Procura em todas as tabelas [cite: 8, 9]
    user = (Instituicao.get_or_none(Instituicao.email == email) or 
            Professor.get_or_none(Professor.email == email) or 
            Aluno.get_or_none(Aluno.email == email))
    
    if user and bcrypt.check_password_hash(user.senha, senha):
        return jsonify({"status": "sucesso", "message": "Login realizado!"}), 200
    
    return jsonify({"status": "erro", "message": "Credenciais inválidas"}), 401

@auth.route('/cadastro/instituicao', methods=['POST'])
def cadastro_instituicao():
    """
    Cadastra uma nova Instituição
    ---
    parameters:
      - name: cnpj
        in: formData
        type: string
        required: true
      - name: nome
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: senha
        in: formData
        type: string
        required: true
    responses:
      201:
        description: Instituição criada
    """
    dados = request.form
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
        # Colunas: CNPJ, nome, email, senha [cite: 9]
        Instituicao.create(
            cnpj=dados.get('cnpj'),
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=senha_hash
        )
        return jsonify({"message": "Instituição cadastrada com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "CNPJ ou E-mail já existe"}), 400

@auth.route('/cadastro/professor', methods=['POST'])
def cadastro_professor():
    """
    Cadastra um novo Professor
    ---
    parameters:
      - name: cpf
        in: formData
        type: string
        required: true
      - name: cnpj_instituicao
        in: formData
        type: string
        required: true
      - name: nome_completo
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: senha
        in: formData
        type: string
        required: true
    responses:
      201:
        description: Professor criado
    """
    dados = request.form
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
        # Colunas: CPF, CNPJ_instituicao_id, nome_completo, email, senha [cite: 8]
        Professor.create(
            cpf=dados.get('cpf'),
            cnpj_instituicao=dados.get('cnpj_instituicao'),
            nome_completo=dados.get('nome_completo'),
            email=dados.get('email'),
            senha=senha_hash
        )
        return jsonify({"message": "Professor cadastrado com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "CPF ou E-mail já existe"}), 400

@auth.route('/cadastro/aluno', methods=['POST'])
def cadastro_aluno():
    """
    Cadastra um novo Aluno
    ---
    parameters:
      - name: cpf
        in: formData
        type: string
        required: true
      - name: cnpj_instituicao
        in: formData
        type: string
        required: true
      - name: nome_completo
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: senha
        in: formData
        type: string
        required: true
      - name: curso
        in: formData
        type: string
        required: true
      - name: turma
        in: formData
        type: string
        required: true
    responses:
      201:
        description: Aluno criado
    """
    dados = request.form
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
        # Colunas: CPF, CNPJ_instituicao_id, nome_completo, email, senha, curso, turma [cite: 9]
        Aluno.create(
            cpf=dados.get('cpf'),
            cnpj_instituicao=dados.get('cnpj_instituicao'),
            nome_completo=dados.get('nome_completo'),
            email=dados.get('email'),
            senha=senha_hash,
            curso=dados.get('curso'),
            turma=dados.get('turma')
        )
        return jsonify({"message": "Aluno cadastrado com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "CPF ou E-mail já existe"}), 400