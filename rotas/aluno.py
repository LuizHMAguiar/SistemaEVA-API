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


@aluno.route('/aluno/avaliacao', methods=['POST'])
def adicionar_avaliacao():
    dados = request.get_json()
    cpf = dados.get('cpf_aluno')
    cod_av = dados.get('cod_avaliacao')

    aluno_obj = Aluno.get_or_none(Aluno.CPF == cpf)
    prova = Avaliacao.get_or_none(Avaliacao.codigo_acesso == cod_av)

    if not aluno_obj or not prova:
        return jsonify({"error": "Aluno ou Avaliação não encontrados"}), 404

    try:
        # get_or_create evita duplicar o início se o aluno recarregar a página
        resp_av = RespostaAvaliacao.create(
            CPF_aluno=cpf,
            ID_avaliacao=prova.ID
        )
        return jsonify({
            "message": "Prova adicionada ao perfil do aluno",
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@aluno.route('/aluno/avaliacoes/<cpf>', methods=['GET'])
def listar_avaliacoes_aluno(cpf):
    try:
        Aluno.get(Aluno.CPF == cpf)
    except Aluno.DoesNotExist:
        return jsonify({"error": "Aluno não encontrado"}), 404
    
    now = datetime.now()
    query = (RespostaAvaliacao
             .select(RespostaAvaliacao, Avaliacao)
             .join(Avaliacao)
             .where(RespostaAvaliacao.CPF_aluno == cpf))

    resultado = []
    for registro in query:
        av = registro.ID_avaliacao
        
        # Garantir que as datas sejam objetos datetime para comparação
        data_inicio = datetime.fromisoformat(str(av.data_inicio)) if isinstance(av.data_inicio, str) else av.data_inicio
        data_fim = datetime.fromisoformat(str(av.data_fim)) if isinstance(av.data_fim, str) else av.data_fim
        
        # Define status baseado no horário atual
        esta_ativa = False
        if data_inicio and data_fim:
            esta_ativa = data_inicio <= now <= data_fim
        
        resultado.append({
            "ID": av.ID,
            "CPF_professor": av.CPF_professor.CPF,
            "titulo": av.titulo,
            "tipo": av.tipo,
            "curso": av.curso,
            "turma": av.turma,
            "disciplina": av.disciplina,
            "data_inicio": data_inicio.isoformat() if data_inicio else None,
            "data_fim": data_fim.isoformat() if data_fim else None,
            "tempo": str(av.tempo),
            "codigo_acesso": av.codigo_acesso,
            "status": "ativa" if esta_ativa else "inativa"
        })
    
    return jsonify(resultado), 200
    
    
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