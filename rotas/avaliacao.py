from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from models.models import Avaliacao

avaliacao = Blueprint('avaliacao', __name__)

@avaliacao.route('/cadastro/avaliacao', methods=['POST'])
def cadastro_avaliacao():
    dados = request.get_json()

    # Verifica se a avaliação já existe
    if Avaliacao.get_or_none(Avaliacao.ID == dados.get('id')):
        return jsonify({"error": "ID já cadastrado"}), 409
    
    # Colunas: ID, CPF_professor, titulo, tipo, curso, turma, disciplina, data_inicio, data_fim, tempo 
    try:
        Avaliacao.create(
            ID=dados.get('id'),
            CPF_professor=dados.get('cpf_professor'),
            titulo=dados.get('titulo'),
            tipo=dados.get('tipo'),
            curso=dados.get('curso'),
            turma=dados.get('turma'),
            disciplina=dados.get('disciplina'),
            data_inicio=dados.get('data_inicio'),
            data_fim=dados.get('data_fim'),
            tempo=dados.get('tempo')
        )
        return jsonify({"message": "Avaliação cadastrada com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "Erro de integridade dos dados"}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao cadastrar avaliação", "details": str(e)}), 500
