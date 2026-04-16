from flask import Blueprint, request, jsonify
from models.models import Questao, QuestaoAvaliacao, Avaliacao, Aluno, RespostaQuestao
from peewee import IntegrityError
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
# Definindo o Blueprint único para questões
questao_bp = Blueprint('questao_bp', __name__)

@questao_bp.route('/questao', methods=['POST'])
@jwt_required()   # Exige autenticação por token
def cadastrar_questao():
    # Obtém o JSON e evita que o servidor trave se o corpo estiver mal formatado ou vazio
    dados = request.get_json(silent=True)
    
    if dados is None:
        return jsonify({"error": "JSON inválido ou corpo da requisição vazio"}), 400

    # Validação de presença do ID da avaliação
    try:
        id_av = int(dados.get('id_avaliacao'))
    except (ValueError, TypeError):
        return jsonify({"error": "ID da avaliação é obrigatório"}), 400
    
    # Verifica se a avaliação existe no banco de dados
    avaliacao = Avaliacao.get_or_none(Avaliacao.ID == id_av)
    if not avaliacao:
        return jsonify({"error": "Avaliação não encontrada"}), 404

    # Daqui para baixo continua o resto da sua lógica de criação...
    # Validação de campos obrigatórios da questão [cite: 73, 77, 81]
    if not dados.get('tipo') or not dados.get('enunciado') or not dados.get('opcao_a') or not dados.get('opcao_b'):
        return jsonify({"error": "Dados obrigatórios não informados: Tipo, Enunciado, Opção A e Opção B são necessários"}), 400

    if dados.get('tipo') not in ['Múltipla Escolha', 'Dissertativa', 'V ou F']:
        return jsonify({"error": "Tipo de questão inválido."}), 400

    try:
        # 1. Salva a questão
        nova_q = Questao.create(
            CPF_professor=dados.get('cpf_professor'),
            ID_avaliacao=id_av,
            tipo=dados.get('tipo'),
            enunciado=dados.get('enunciado'),
            opcao_a=dados.get('opcao_a'),
            opcao_b=dados.get('opcao_b'),
            opcao_c=dados.get('opcao_c'),
            opcao_d=dados.get('opcao_d'),
            opcao_e=dados.get('opcao_e')
        )

        # 2. Cria o vínculo na tabela associativa [cite: 191, 194, 198]
        QuestaoAvaliacao.create(
            ID_questao=nova_q.ID,
            ID_avaliacao=id_av
        )

        return jsonify({"message": "Questão criada e vinculada com sucesso!", "id": nova_q.ID}), 201
    except Exception as e:
        return jsonify({"error": "Erro ao criar questão", "details": str(e)}), 500

@questao_bp.route('/avaliacao/vincular-existente', methods=['POST'])
@jwt_required()   # Exige autenticação por token
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
@jwt_required()   # Exige autenticação por token
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

@questao_bp.route('/questao/responder', methods=['POST'])
@jwt_required()   # Exige autenticação por token
def responder_questao():
    """Recebe respostas em texto e/ou áudio (multipart/form-data) [cite: 180, 184]"""
    dados = request.get_json()
    cpf_aluno = dados.get('cpf_aluno')
    id_avaliacao = dados.get('id_avaliacao')
    id_questao = dados.get('id_questao')
    texto_resposta = dados.get('resposta')

    # 1. Verificar se o aluno existe
    aluno = Aluno.get_or_none(Aluno.CPF == cpf_aluno)
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 401

    # 2. Verificar se a avaliação existe e está no prazo
    avaliacao = Avaliacao.get_or_none(Avaliacao.ID == id_avaliacao)
    if not avaliacao:
        return jsonify({"error": "Avaliação não encontrada"}), 404
    
    agora = datetime.now()
    if agora < avaliacao.data_inicio or agora > avaliacao.data_fim:
        return jsonify({"error": "Esta avaliação não está disponível no momento (fora do prazo)"}), 403

    # 3. Verificar se a questão existe e pertence à avaliação
    vinculo = QuestaoAvaliacao.get_or_none((QuestaoAvaliacao.ID_questao == id_questao) & 
                                           (QuestaoAvaliacao.ID_avaliacao == id_avaliacao))
    if not vinculo:
        return jsonify({"error": "Esta questão não pertence à avaliação informada"}), 400

    try:
        resposta_obj, created = RespostaQuestao.get_or_create(
            CPF_aluno_id=cpf_aluno,
            ID_avaliacao_id=id_avaliacao,
            ID_questao_id=id_questao,
            defaults={'resposta': texto_resposta or ""}
        )

        if not created and texto_resposta is not None:
            resposta_obj.resposta = texto_resposta
        
        resposta_obj.save()

        return jsonify({"message": "Resposta salva com sucesso!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@questao_bp.route('/provas_disponibilidade/<cpf_aluno>', methods=['GET'])
@jwt_required()   # Exige autenticação por token
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