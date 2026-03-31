from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao, Aluno, Avaliacao, RespostaAvaliacao, RespostaQuestao, QuestaoAvaliacao
from datetime import datetime

aluno = Blueprint('aluno', __name__)
bcrypt = Bcrypt()

# --- ROTAS DE GESTÃO DO ALUNO (CRUD) ---

@aluno.route('/aluno', methods=['POST'])
def cadastro_aluno():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Formato inválido do body da requisição JSON"}), 400
    
    if Aluno.get_or_none(Aluno.CPF == dados.get('cpf')):
        return jsonify({"error": "CPF já cadastrado"}), 409
    
    if Aluno.get_or_none(Aluno.email == dados.get('email')):
        return jsonify({"error": "E-mail já cadastrado"}), 409
    
    if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('cnpj_instituicao')) is None:
        return jsonify({"error": "Instituição não cadastrada"}), 400
    
    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    
    try:
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

@aluno.route('/aluno', methods=['GET'])
def listar_alunos():
    alunos = Aluno.select()
    return jsonify([{
        "cpf": a.CPF,
        "cnpj_instituicao": a.CNPJ_instituicao.CNPJ,
        "nome_completo": a.nome_completo,
        "email": a.email,
        "curso": a.curso,
        "turma": a.turma
    } for a in alunos]), 200

@aluno.route('/aluno/<string:cpf>', methods=['GET'])
def buscar_aluno_por_cpf(cpf):
    try:
        a = Aluno.get(Aluno.CPF == cpf)
        return jsonify({
            "cpf": a.CPF,
            "cnpj_instituicao": a.CNPJ_instituicao.CNPJ,
            "nome_completo": a.nome_completo,
            "email": a.email,
            "curso": a.curso,
            "turma": a.turma
        }), 200
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404

@aluno.route('/aluno/<cpf>', methods=['DELETE'])
def deletar_aluno(cpf):
    try:
        aluno_obj = Aluno.get(Aluno.CPF == cpf)
        aluno_obj.delete_instance()
        return jsonify({"message": "Aluno deletado com sucesso!"}), 200
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404

@aluno.route('/aluno/<cpf>', methods=['PATCH'])
def atualizar_aluno(cpf):
    try:
        aluno_obj = Aluno.get(Aluno.CPF == cpf)
        dados = request.get_json()
        
        if 'nome_completo' in dados: aluno_obj.nome_completo = dados['nome_completo']
        if 'curso' in dados: aluno_obj.curso = dados['curso']
        if 'turma' in dados: aluno_obj.turma = dados['turma']
        if 'email' in dados:
            existente = Aluno.get_or_none(Aluno.email == dados['email'])
            if existente and existente.CPF != cpf:
                return jsonify({"error": "E-mail já cadastrado"}), 409
            aluno_obj.email = dados['email']
        if 'senha' in dados:
            aluno_obj.senha = bcrypt.generate_password_hash(dados['senha']).decode('utf-8')
        
        aluno_obj.save()
        return jsonify({"message": "Aluno atualizado com sucesso!"}), 200
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404


    
#@questao_bp.route('/audio_enunciado/<int:id_questao>', methods=['GET'])
#def ouvir_enunciado(id_questao):
#    questao = Questao.get_or_none(Questao.ID == id_questao)
#    
#    if not questao or not questao.audio_enunciado:
#        return jsonify({"error": "Esta questão não possui áudio."}), 404
#
#    return send_file(
 #       io.BytesIO(questao.audio_enunciado),
#        mimetype='audio/webm'
 #   )