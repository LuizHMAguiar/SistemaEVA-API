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

# --- ROTAS DE FLUXO DE AVALIAÇÃO ---

@aluno.route('/avaliacao/iniciar', methods=['POST'])
def iniciar_prova():
    dados = request.get_json()
    cpf = dados.get('cpf_aluno')
    id_av = dados.get('id_avaliacao')

    aluno_obj = Aluno.get_or_none(Aluno.CPF == cpf)
    prova = Avaliacao.get_or_none(Avaliacao.ID == id_av)

    if not aluno_obj or not prova:
        return jsonify({"error": "Aluno ou Avaliação não encontrados"}), 404

    try:
        # get_or_create evita duplicar o início se o aluno recarregar a página
        resp_av, created = RespostaAvaliacao.get_or_create(
            CPF_aluno=cpf,
            ID_avaliacao=id_av,
            defaults={'data_hora_inicio': datetime.now()}
        )
        return jsonify({
            "message": "Prova iniciada", 
            "data_inicio": resp_av.data_hora_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "reutilizado": not created
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@aluno.route('/avaliacao/responder-questao', methods=['POST'])
def responder_questao():
    dados = request.get_json()
    cpf = dados.get('cpf_aluno')
    id_av = dados.get('id_avaliacao')
    id_q = dados.get('id_questao')
    resp_texto = dados.get('resposta')

    # Valida se a questão pertence à prova
    if not QuestaoAvaliacao.get_or_none((QuestaoAvaliacao.ID_avaliacao == id_av) & (QuestaoAvaliacao.ID_questao == id_q)):
        return jsonify({"error": "Questão não pertence a esta avaliação"}), 400

    try:
        resposta, created = RespostaQuestao.get_or_create(
            CPF_aluno=cpf,
            ID_avaliacao=id_av,
            ID_questao=id_q,
            defaults={'resposta': resp_texto}
        )
        if not created:
            resposta.resposta = resp_texto
            resposta.save()
        return jsonify({"message": "Resposta salva"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@aluno.route('/avaliacao/finalizar', methods=['POST'])
def finalizar_prova():
    dados = request.get_json()
    cpf = dados.get('cpf_aluno')
    id_av = dados.get('id_avaliacao')

    try:
        registro = RespostaAvaliacao.get_or_none(
            (RespostaAvaliacao.CPF_aluno == cpf) & (RespostaAvaliacao.ID_avaliacao == id_av)
        )

        if not registro:
            return jsonify({"error": "Início de prova não registrado"}), 404
        if registro.data_hora_fim:
            return jsonify({"message": "Avaliação já finalizada"}), 200

        agora = datetime.now()
        registro.data_hora_fim = agora
        
        # Cálculo de tempo decorrido
        inicio = registro.data_hora_inicio
        if isinstance(inicio, str):
            inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
        
        delta = agora - inicio
        horas, resto = divmod(delta.total_seconds(), 3600)
        minutos, segundos = divmod(resto, 60)
        registro.tempo_corrido = f"{int(horas):02d}:{int(minutos):02d}:{int(segundos):02d}"

        registro.save()
        return jsonify({
            "message": "Finalizada",
            "tempo_total": registro.tempo_corrido
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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