from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from models.models import Avaliacao, Instituicao, Professor

instituicao = Blueprint('instituicao', __name__)
@instituicao.route('/cadastro/instituicao', methods=['POST'])
def cadastro_instituicao():
    dados = request.get_json()
    
    try:
        nova_instituicao = Instituicao.create(
            CNPJ=dados.get('cnpj'),
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=dados.get('senha')
        )
        
        return jsonify({
            "message": "Instituição cadastrada com sucesso!",
            "cnpj_gerado": nova_instituicao.CNPJ
        }), 201

    except IntegrityError:
        return jsonify({"error": "Erro de integridade: verifique os dados enviados"}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500