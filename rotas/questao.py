from flask import Blueprint, request, jsonify
from models.models import Questao, QuestaoAvaliacao, RespostaQuestao, Aluno, Avaliacao
from datetime import datetime

# Definindo o nome padrão para evitar erros de NameError
questao_bp = Blueprint('questoes', __name__)

@questao_bp.route('/cadastro/questoes', methods=['POST'])
def cadastrar_questao():

    dados = request.get_json()
    try:
        # 1 -> Salva a questão com suas opções
        nova_q = Questao.create(
            tipo=dados.get('tipo'),
            enunciado=dados.get('enunciado'),
            opcao_a=dados.get('opcoes', {}).get('a'),
            opcao_b=dados.get('opcoes', {}).get('b'),
            opcao_c=dados.get('opcoes', {}).get('c'),
            opcao_d=dados.get('opcoes', {}).get('d'),
            opcao_e=dados.get('opcoes', {}).get('e')
        )

        # 2 -> Cria o vínculo na tabela associativa QuestaoAvaliacao
        QuestaoAvaliacao.create(
            ID_questao=nova_q.ID,
            ID_avaliacao=dados.get('id_avaliacao')
        )

        return jsonify({"message": "Questão criada e vinculada!", "id": nova_q.ID}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/responder', methods=['POST'])
def responder_questao():

    cpf_aluno = request.form.get('cpf_aluno')
    id_avaliacao = request.form.get('id_avaliacao')
    id_questao = request.form.get('id_questao')
    texto_resposta = request.form.get('resposta')
    arquivo_audio = request.files.get('audio')

    try:
        audio_blob = arquivo_audio.read() if arquivo_audio else None

        RespostaQuestao.create(
            CPF_aluno=cpf_aluno,
            ID_avaliacao=id_avaliacao,
            ID_questao=id_questao,
            resposta=texto_resposta,
            audio_resposta=audio_blob
        )

        return jsonify({"message": "Resposta salva com sucesso!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/provas_disponibilidade/<cpf_aluno>', methods=['GET'])
def provas_disponiveis(cpf_aluno):

    aluno = Aluno.get_or_none(Aluno.CPF == cpf_aluno)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    agora = datetime.now()

    provas = Avaliacao.select().where(
        (Avaliacao.curso == aluno.curso) &
        (Avaliacao.turma == aluno.turma) &
        (Avaliacao.data_inicio <= agora) &
        (Avaliacao.data_fim >= agora)
    )

    return jsonify([{
        "id": p.ID,
        "titulo": p.titulo,
        "disciplina": p.disciplina,
        "tempo_limite": str(p.tempo)
    } for p in provas]), 200