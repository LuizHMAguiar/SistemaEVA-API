from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from flask_bcrypt import Bcrypt
from flask import send_file
import io
from models.models import Instituicao, Professor, RespostaQuestao, Questao

professor = Blueprint('professor', __name__)
bcrypt = Bcrypt()


@professor.route('/professor', methods=['POST'])
def cadastro_professor():
    dados = request.get_json()

    if Professor.get_or_none(Professor.CPF == dados.get('cpf')):
      return jsonify({"error": "CPF já cadastrado"}), 409
    
    if Professor.get_or_none(Professor.email == dados.get('email')):
      return jsonify({"error": "E-mail já cadastrado"}), 409

    # Verificar se a chave estrangeira corresponde a uma PK existente na outra tabela. 
    # TODO: Fazer isso para todas
    if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('cnpj_instituicao')) == None:
      return jsonify({"error": "Instituição não cadastrada"}), 400


    senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
    try:
        # Colunas: CPF, CNPJ_instituicao_id, nome_completo, email, senha [cite: 8]
        Professor.create(
            CPF=dados.get('cpf'),
            CNPJ_instituicao=dados.get('cnpj_instituicao'),
            nome_completo=dados.get('nome_completo'),
            email=dados.get('email'),
            senha=senha_hash
        )
        return jsonify({"message": "Professor cadastrado com sucesso!"}), 201
    except IntegrityError:
        return jsonify({"error": "Erro de integridade"}), 400
    
@professor.route('/professor', methods=['GET'])
def listar_professores():
    professores  = Professor.select()
    resultado = []
    
    for professor in professores:
        resultado.append({
            "CPF": professor.CPF,
            "CNPJ_instituicao": professor.CNPJ_instituicao.CNPJ,
            "nome_completo": professor.nome_completo,
            "email": professor.email,
        })   
    return jsonify(resultado), 200

@professor.route('/professor/<string:cpf>', methods=['GET'])
def buscar_professor_por_cpf(cpf):
    try:
        professor = Professor.get(Professor.CPF == cpf)
        resultado = {
            "CPF": professor.CPF,
            "CNPJ_instituicao": professor.CNPJ_instituicao.CNPJ,
            "nome_completo": professor.nome_completo,
            "email": professor.email,
        }
        return jsonify(resultado), 200
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar professor", "details": str(e)}), 500

@professor.route('/professor/<string:cpf>', methods=['DELETE'])
def excluir_professor(cpf):
    try:
        professor = Professor.get(Professor.CPF == cpf)
        professor.delete_instance()
        return jsonify({"message": "Professor excluído com sucesso!"}), 200
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao excluir professor", "details": str(e)}), 500
        
@professor.route('/professor/<string:cpf>', methods=['PATCH'])
def atualizar_professor(cpf):
    dados = request.get_json()
    try:
        professor = Professor.get(Professor.CPF == cpf)
        
        if'CNPJ_instituicao' in dados:
            if Instituicao.get_or_none(Instituicao.CNPJ == dados.get('CNPJ_instituicao')) == None:
                return jsonify({"error": "Instituição não cadastrada"}), 400
            professor.CNPJ_instituicao = dados.get('CNPJ_instituicao')

        if 'email' in dados:
            if Professor.get_or_none(Professor.email == dados.get('email')):
                return jsonify({"error": "E-mail já cadastrado"}), 409
            professor.email = dados.get('email')

        if 'nome_completo' in dados:
            professor.nome_completo = dados.get('nome_completo')

        if 'senha' in dados:
            senha_hash = bcrypt.generate_password_hash(dados.get('senha')).decode('utf-8')
            professor.senha = senha_hash

        professor.save()
        return jsonify({"message": "Professor atualizado com sucesso!"})
    except Professor.DoesNotExist:
        return jsonify({"error": "Professor não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar professor", "details": str(e)}), 500
from models.models import RespostaAvaliacao, Aluno, Avaliacao

@professor.route('/relatorio/avaliacao/<int:id_avaliacao>', methods=['GET'])
def relatorio_avaliacao(id_avaliacao):
    try:
        # Busca todas as respostas daquela avaliação específica
        respostas = (RespostaAvaliacao
                     .select(RespostaAvaliacao, Aluno)
                     .join(Aluno)
                     .where(RespostaAvaliacao.ID_avaliacao == id_avaliacao))

        if not respostas:
            return jsonify({"message": "Nenhum aluno iniciou esta avaliação ainda."}), 200

        resultado = []
        for r in respostas:
            resultado.append({
                "nome_aluno": r.CPF_aluno.nome_completo,
                "cpf": r.CPF_aluno.CPF,
                "inicio": r.data_hora_inicio.strftime("%d/%m/%Y %H:%M:%S") if r.data_hora_inicio else None,
                "fim": r.data_hora_fim.strftime("%d/%m/%Y %H:%M:%S") if r.data_hora_fim else "Em andamento",
                "tempo_total": r.tempo_corrido or "Pendente"
            })

        return jsonify({
            "avaliacao_id": id_avaliacao,
            "total_alunos": len(resultado),
            "participantes": resultado
        }), 200

    except Exception as e:
        return jsonify({"error": "Erro ao gerar relatório", "details": str(e)}), 500 

@professor.route('/relatorio/aluno/<string:cpf_aluno>/avaliacao/<int:id_avaliacao>', methods=['GET'])
def detalhe_respostas_aluno(cpf_aluno, id_avaliacao):
    try:
        # Busca as respostas vinculadas ao aluno e avaliação, trazendo os dados da questão
        respostas = (RespostaQuestao
                     .select(RespostaQuestao, Questao)
                     .join(Questao)
                     .where((RespostaQuestao.CPF_aluno == cpf_aluno) & 
                            (RespostaQuestao.ID_avaliacao == id_avaliacao)))

        if not respostas:
            return jsonify({"message": "Nenhuma resposta encontrada para este aluno nesta avaliação."}), 404

        detalhes = []
        for r in respostas:
            detalhes.append({
                "questao_id": r.ID_questao.ID,
                "enunciado": r.ID_questao.enunciado,
                "tipo_questao": r.ID_questao.tipo,
                "resposta_texto": r.resposta,
                "tem_audio": True if r.audio_resposta else False
            })

        return jsonify({
            "cpf_aluno": cpf_aluno,
            "id_avaliacao": id_avaliacao,
            "respostas": detalhes
        }), 200

    except Exception as e:
        return jsonify({"error": "Erro ao buscar detalhes das respostas", "details": str(e)}), 500


@professor.route('/audio/<string:cpf>/<int:id_av>/<int:id_q>', methods=['GET'])
def buscar_audio_resposta(cpf, id_av, id_q):
    try:
        # Busca a resposta específica que contém o arquivo de áudio
        resposta = RespostaQuestao.get_or_none(
            (RespostaQuestao.CPF_aluno == cpf) & 
            (RespostaQuestao.ID_avaliacao == id_av) & 
            (RespostaQuestao.ID_questao == id_q)
        )

        if not resposta or not resposta.audio_resposta:
            return jsonify({"error": "Áudio não encontrado para esta questão."}), 404

        # Transforma o binário do banco em um "arquivo virtual" na memória
        return send_file(
            io.BytesIO(resposta.audio_resposta),
            mimetype='audio/webm', # Ou 'audio/mpeg' dependendo de como o front grava
            as_attachment=False,
            download_name=f"resposta_{cpf}_{id_q}.webm"
        )

    except Exception as e:
        return jsonify({"error": "Erro ao recuperar áudio", "details": str(e)}), 500    