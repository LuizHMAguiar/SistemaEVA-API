from flask import Blueprint, request, jsonify
from models.models import Questao, QuestaoAvaliacao, Avaliacao, Aluno, RespostaQuestao
from peewee import IntegrityError
from datetime import datetime

# Definindo o Blueprint único para questões
questao_bp = Blueprint('questao_bp', __name__)

@questao_bp.route('/cadastro/questoes', methods=['POST'])
def cadastrar_questao():
    # Obtém o JSON e evita que o servidor trave se o corpo estiver mal formatado ou vazio
    dados = request.get_json(silent=True)
    
    if dados is None:
        return jsonify({"error": "JSON inválido ou corpo da requisição vazio"}), 400

    # Validação de presença do ID da avaliação
    id_av = dados.get('id_avaliacao')
    if not id_av:
        return jsonify({"error": "ID da avaliação é obrigatório"}), 400
    
    # Verifica se a avaliação existe no banco de dados
    avaliacao = Avaliacao.get_or_none(Avaliacao.ID == id_av)
    if not avaliacao:
        return jsonify({"error": "Avaliação não encontrada"}), 404

    # Daqui para baixo continua o resto da sua lógica de criação...
    # Validação de campos obrigatórios da questão [cite: 73, 77, 81]
    opcoes = dados.get('opcoes', {})
    if not dados.get('tipo') or not dados.get('enunciado') or not opcoes.get('a') or not opcoes.get('b'):
        return jsonify({"error": "Dados obrigatórios não informados: Tipo, Enunciado, Opção A e Opção B são necessários"}), 400

    if dados.get('tipo') not in ['Múltipla Escolha', 'Dissertativa', 'V ou F']:
        return jsonify({"error": "Tipo de questão inválido."}), 400

    try:
        # 1. Salva a questão [cite: 70, 73, 85, 89]
        nova_q = Questao.create(
            tipo=dados.get('tipo'),
            enunciado=dados.get('enunciado'),
            opcao_a=opcoes.get('a'),
            opcao_b=opcoes.get('b'),
            opcao_c=opcoes.get('c'),
            opcao_d=opcoes.get('d'),
            opcao_e=opcoes.get('e')
        )

        # 2. Cria o vínculo na tabela associativa [cite: 191, 194, 198]
        QuestaoAvaliacao.create(
            ID_questao=nova_q.ID,
            ID_avaliacao=dados.get('id_avaliacao')
        )

        return jsonify({"message": "Questão criada e vinculada com sucesso!", "id": nova_q.ID}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao criar questão", "details": str(e)}), 500

@questao_bp.route('/avaliacao/vincular-existente', methods=['POST'])
def vincular_questao_existente():
    """Rota para reaproveitar uma questão em uma nova avaliação"""
    dados = request.get_json()
    id_q = dados.get('id_questao')
    id_av = dados.get('id_avaliacao')

    if not id_q or not id_av:
        return jsonify({"error": "ID da questão e da avaliação são necessários"}), 400

    try:
        QuestaoAvaliacao.create(ID_questao=id_q, ID_avaliacao=id_av)
        return jsonify({"message": "Questão reaproveitada com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "Esta questão já está vinculada a esta avaliação"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/avaliacao/<int:id_avaliacao>/questoes', methods=['GET'])
def listar_questoes_da_avaliacao(id_avaliacao):
    """Lista todas as questões vinculadas a uma avaliação específica"""
    try:
        # Busca questões fazendo join com a tabela de questões [cite: 191, 144]
        questoes = (Questao.select()
                    .join(QuestaoAvaliacao)
                    .where(QuestaoAvaliacao.ID_avaliacao == id_avaliacao))

        resultado = []
        for q in questoes:
            resultado.append({
                "id": q.ID,
                "tipo": q.tipo,
                "enunciado": q.enunciado,
                "opcoes": {"a": q.opcao_a, "b": q.opcao_b, "c": q.opcao_c, "d": q.opcao_d, "e": q.opcao_e}
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/responder', methods=['POST'])
def responder_questao():
    """Recebe respostas em texto e/ou áudio (multipart/form-data) [cite: 180, 184]"""
    cpf_aluno = request.form.get('cpf_aluno')
    id_avaliacao = request.form.get('id_avaliacao')
    id_questao = request.form.get('id_questao')
    texto_resposta = request.form.get('resposta')
    arquivo_audio = request.files.get('audio')

    try:
        audio_blob = arquivo_audio.read() if arquivo_audio else None

        # Salva ou atualiza a resposta do aluno [cite: 164, 168, 172, 176]
        resposta_obj, created = RespostaQuestao.get_or_create(
            CPF_aluno=cpf_aluno,
            ID_avaliacao=id_avaliacao,
            ID_questao=id_questao,
            defaults={'resposta': texto_resposta, 'audio_resposta': audio_blob}
        )

        if not created:
            resposta_obj.resposta = texto_resposta
            if audio_blob:
                resposta_obj.audio_resposta = audio_blob
            resposta_obj.save()

        return jsonify({"message": "Resposta salva com sucesso!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/provas_disponibilidade/<cpf_aluno>', methods=['GET'])
def provas_disponiveis(cpf_aluno):
    """Lista provas baseadas no curso/turma do aluno e no horário atual [cite: 19, 23, 131, 135]"""
    aluno = Aluno.get_or_none(Aluno.CPF == cpf_aluno)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    agora = datetime.now()

    # Filtra por curso, turma e janela de tempo [cite: 20, 123, 134, 138]
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