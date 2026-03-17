from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao, Aluno

aluno = Blueprint('aluno', __name__)
bcrypt = Bcrypt()

@aluno.route('/aluno', methods=['POST'])
def cadastro_aluno():
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

@aluno.route('/aluno', methods=['GET'])
def listar_alunos():
    alunos = Aluno.select()
    resultado = []
    
    for aluno in alunos:
        resultado.append({
            "cpf": aluno.CPF,
            "cnpj_instituicao": aluno.CNPJ_instituicao.CNPJ,
            "nome_completo": aluno.nome_completo,
            "email": aluno.email,
            "curso": aluno.curso,
            "turma": aluno.turma
        })
    
    return jsonify(resultado), 200

@aluno.route('/aluno/<string:cpf>', methods=['GET'])
def buscar_aluno_por_cpf(cpf):
    try:
        aluno = Aluno.get(Aluno.CPF == cpf)
        resultado = {
            "cpf": aluno.CPF,
            "cnpj_instituicao": aluno.CNPJ_instituicao.CNPJ,
            "nome_completo": aluno.nome_completo,
            "email": aluno.email,
            "curso": aluno.curso,
            "turma": aluno.turma
        }
        return jsonify(resultado), 200
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar aluno", "details": str(e)}), 500



@aluno.route('/aluno/<cpf>', methods=['DELETE'])
def deletar_aluno(cpf):
    try:
        aluno = Aluno.get(Aluno.CPF == cpf)
        aluno.delete_instance()
        return jsonify({"message": "Aluno deletado com sucesso!"}), 200
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao deletar aluno", "details": str(e)}), 500

@aluno.route('/aluno/<cpf>', methods=['PATCH'])
def atualizar_aluno(cpf):
    try:
        aluno = Aluno.get(Aluno.CPF == cpf)
        dados = request.get_json()
        
        if dados is None:
            return jsonify({"error": "Formato inválido do body da requisição JSON"}), 400
        
        # Atualizar campos opcionais
        if 'nome_completo' in dados:
            aluno.nome_completo = dados.get('nome_completo')
        if 'email' in dados:
            # Verificar se o novo email já existe
            if Aluno.get_or_none(Aluno.email == dados.get('email')) and Aluno.get_or_none(Aluno.email == dados.get('email')).CPF != cpf:
                return jsonify({"error": "E-mail já cadastrado"}), 409
            aluno.email = dados.get('email')
        if 'curso' in dados:
            aluno.curso = dados.get('curso')
        if 'turma' in dados:
            aluno.turma = dados.get('turma')
        if 'senha' in dados:
            senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
            aluno.senha = senha_hash
        
        aluno.save()
        return jsonify({"message": "Aluno atualizado com sucesso!"}), 200
    
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar aluno", "details": str(e)}), 500

