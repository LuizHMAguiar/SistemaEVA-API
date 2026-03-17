from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from models.models import Avaliacao, Instituicao, Professor

avaliacao = Blueprint('avaliacao', __name__)

@avaliacao.route('/avaliacao', methods=['POST'])
def cadastro_avaliacao():
    dados = request.get_json()
    
    try:
        # 1. Validação de Integridade: Verifica se o Professor existe
        # Nota: Usamos Professor.CPF (maiúsculo) conforme o seu models.py
        professor_existente = Professor.get_or_none(Professor.CPF == dados.get('cpf_professor'))
        
        if professor_existente is None:
            # O 'return' aqui impede que qualquer código abaixo (incluindo o .create) seja executado
            return jsonify({"error": "CPF do professor não encontrado no sistema"}), 400
        
        # 2. Criação: Só será executado se o professor acima EXISTIR
        nova_avaliacao = Avaliacao.create(
            # ID é AutoField, então não é obrigatório enviar, mas mantemos se desejar manual
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
        
        return jsonify({
            "message": "Avaliação cadastrada com sucesso!",
            "id_gerado": nova_avaliacao.ID
        }), 201

    except IntegrityError:
        # Captura erros como violação de chave estrangeira se o banco de dados barrar
        return jsonify({"error": "Erro de integridade: verifique os dados enviados"}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500
@avaliacao.route('/avaliacao', methods=['GET'])
def listar_avaliacoes():
    avaliacoes = Avaliacao.select()
    resultado = []
    
    for avaliacao in avaliacoes:
        resultado.append({
            "id": avaliacao.ID,
            "cpf_professor": avaliacao.CPF_professor.CPF, 
            "titulo": avaliacao.titulo,
            "tipo": avaliacao.tipo,
            "curso": avaliacao.curso,
            "turma": avaliacao.turma,
            "disciplina": avaliacao.disciplina,
            "data_inicio": str(avaliacao.data_inicio), # Converter data para texto
            "data_fim": str(avaliacao.data_fim),       # Converter data para texto
            "tempo": str(avaliacao.tempo)              # Converter tempo para texto
        })
        
    return jsonify(resultado), 200

@avaliacao.route('/avaliacao/<int:id>', methods=['GET'])
def buscar_avaliacao_por_id(id):
    try:
        avaliacao = Avaliacao.get(Avaliacao.ID == id)
        resultado = {
            "id": avaliacao.ID,
            "cpf_professor": avaliacao.CPF_professor.CPF,
            "titulo": avaliacao.titulo,
            "tipo": avaliacao.tipo,
            "curso": avaliacao.curso,
            "turma": avaliacao.turma,
            "disciplina": avaliacao.disciplina,
            "data_inicio": str(avaliacao.data_inicio),
            "data_fim": str(avaliacao.data_fim),
            "tempo": str(avaliacao.tempo)
        }
        return jsonify(resultado), 200
    except Avaliacao.DoesNotExist:
        return jsonify({"error": "Avaliação não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar avaliação", "details": str(e)}), 500

@avaliacao.route('/avaliacao/<int:id>', methods=['DELETE'])
def excluir_avaliacao(id):
    try:
        avaliacao_obj = Avaliacao.get(Avaliacao.ID == id)
        avaliacao_obj.delete_instance()
        return jsonify({"message": "Avaliação excluída com sucesso!"}), 200
    except Avaliacao.DoesNotExist:
        return jsonify({"error": "Avaliação não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao excluir avaliação", "details": str(e)}), 500

