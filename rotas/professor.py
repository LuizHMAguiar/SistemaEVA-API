from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from flask_bcrypt import Bcrypt
from models.models import Avaliacao, Instituicao, Professor

professor = Blueprint('professor', __name__)

@professor.route('/professor', methods=['POST'])
def cadastro_professor():
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
    
@professor.route('/professor', methods=['GET'])
def listar_professores():
    professores  = Professor.select()
    resultado = []
    
    for professor in professores:
        resultado.append({
            "CPF": professor.CPF,
            "CNPJ_instituicao": professor.CNPJ_instituicao.CNPJ,
            "nome_completo": professor.nome_completo,
            "email": professor.email,
            "senha": professor.senha
        })   
    return jsonify(resultado), 200

@professor.route('/professor/<string:cpf>', methods=['GET'])
def buscar_professor_por_cpf(cpf):
    try:
        professor = Professor.get(Professor.CPF == cpf)
        resultado = {
            "CPF": professor.CPF,
            "CNPJ_instituicao": professor.CNPJ_instituicao.CNPJ,
            "nome_completo": professor.nome_completo,
            "email": professor.email,
            "senha": professor.senha
        }
        return jsonify(resultado), 200
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar professor", "details": str(e)}), 500

@professor.route('/professor/<string:cpf>', methods=['DELETE'])
def excluir_professor(cpf):
    try:
        professor = Professor.get(Professor.CPF == cpf)
        professor.delete_instance()
        return jsonify({"message": "Professor excluído com sucesso!"}), 200
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao excluir professor", "details": str(e)}), 500
        
@professor.route('/professor/<string:cpf>', methods=['PATCH'])
def atualizar_professor(cpf):
    dados = request.get_json()
    try:
        professor = Professor.get(Professor.CPF == cpf)
        
        if'CNPJ_instituicao' in dados:
            if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('CNPJ_instituicao')) == None:
                return jsonify({"error": "Instituição não cadastrada"}), 400
            professor.CNPJ_instituicao = dados.get('CNPJ_instituicao')

        if 'email' in dados:
            if Professor.get_or_none(Professor.email == dados.get('email')):
                return jsonify({"error": "E-mail já cadastrado"}), 409
            professor.email = dados.get('email')

        if 'nome_completo' in dados:
            professor.nome_completo = dados.get('nome_completo')

        if 'senha' in dados:
            senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
            professor.senha = senha_hash

        professor.save()
        return jsonify({"message": "Professor atualizado com sucesso!"})
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar professor", "details": str(e)}), 500
        