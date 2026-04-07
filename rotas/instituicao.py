from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from peewee import IntegrityError
from models.models import Instituicao

instituicao = Blueprint('instituicao', __name__)
bcrypt = Bcrypt()

#13 faz o cadastro da instituição, não podendo repitir o cnpj é o email.

@instituicao.route('/instituicao', methods=['POST'])
def cadastro_instituicao():
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
    
#13 Lista tudas as instituições já criadas.

@instituicao.route('/instituicao', methods=['GET'])
def listar_instituicoes():  
    instituicoes = Instituicao.select()
    lista_instituicoes = []
    for instituicao in instituicoes:
        lista_instituicoes.append({
            "cnpj": instituicao.CNPJ,
            "nome": instituicao.nome,
            "email": instituicao.email
        })
    return jsonify(lista_instituicoes), 200

#13 Lista uma intituição pelo cnpj da instituição.

@instituicao.route('/instituicao/<int:instituicao_cnpj>', methods=['GET'])
def obter_instituicao(instituicao_cnpj):
    instituicao = Instituicao.get_or_none(Instituicao.CNPJ == instituicao_cnpj)
    if not instituicao:
        return jsonify({"error": "Instituição não encontrada"}), 404
    return jsonify({
        "cnpj": instituicao.CNPJ,
        "nome": instituicao.nome,
        "email": instituicao.email 
    }), 200

#13 Atualiza instituição pelo cnpj, não podendo fazer modificação no propio cnpj.

@instituicao.route('/instituicao/<string:instituicao_cnpj>', methods=['PATCH'])
def atualizar_instituicao(instituicao_cnpj):
    # No modelo Instituicao, a chave primária é o CNPJ (CharField)
    instituicao = Instituicao.get_or_none(Instituicao.CNPJ == instituicao_cnpj)
    
    if not instituicao:
        return jsonify({"error": "Instituição não encontrada"}), 404
    
    dados = request.get_json()
    
    # Atualiza os campos fornecidos
    if 'nome' in dados:
        instituicao.nome = dados['nome']
    if 'email' in dados:
        instituicao.email = dados['email']
    if 'senha' in dados:
        senha_hash = bcrypt.generate_password_hash(dados['senha']).decode('utf-8')
        instituicao.senha = senha_hash
    
    try:
        instituicao.save()
        return jsonify({"message": "Instituição atualizada com sucesso!"}), 200
    except IntegrityError:
        return jsonify({"error": "Erro de integridade dos dados"}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar instituição", "details": str(e)}), 500
    
#13 Deleta uma instituição pelo cnpj.

@instituicao.route('/instituicao/<int:instituicao_cnpj>', methods=['DELETE'])
def deletar_instituicao(instituicao_cnpj):
    instituicao = Instituicao.get_or_none(Instituicao.CNPJ == instituicao_cnpj)
    if not instituicao:
        return jsonify({"error": "Instituição não encontrada"}), 404
    
    try:
        instituicao.delete_instance()
        return jsonify({"message": "Instituição deletada com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": "Erro ao deletar instituição", "details": str(e)}), 500