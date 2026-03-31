from flask import Blueprint, request, jsonify
from peewee import IntegrityError
from models.models import Avaliacao, Instituicao, Professor, Aluno, RespostaAvaliacao, RespostaQuestao, QuestaoAvaliacao
from datetime import datetime
import datetime as dt

avaliacao = Blueprint('avaliacao', __name__)

@avaliacao.route('/avaliacao', methods=['POST'])
def cadastro_avaliacao():
    dados = request.get_json()
    
    try:
        # 1. Validação de Integridade: Verifica se o Professor existe [cite: 102, 103]
        professor_existente = Professor.get_or_none(Professor.CPF == dados.get('cpf_professor'))
        
        if professor_existente is None:
            return jsonify({"error": "CPF do professor não encontrado no sistema"}), 400
        
        # 2. Criação: Adicionamos o campo codigo_acesso [cite: 102, 103]
        nova_avaliacao = Avaliacao.create(
            ID=dados.get('id'), 
            CPF_professor=dados.get('cpf_professor'),
            titulo=dados.get('titulo'),
            tipo=dados.get('tipo'),
            curso=dados.get('curso'),
            turma=dados.get('turma'),
            disciplina=dados.get('disciplina'),
            data_inicio=dados.get('data_inicio'),
            data_fim=dados.get('data_fim'),
            tempo=dados.get('tempo'), # Adicionada a vírgula aqui!
            codigo_acesso=dados.get('codigo_acesso')
        )
        
        return jsonify({
            "message": "Avaliação cadastrada com sucesso!",
            "id_gerado": nova_avaliacao.ID, # Adicionada a vírgula aqui!
            "codigo_acesso": nova_avaliacao.codigo_acesso
        }), 201

    except IntegrityError:
        return jsonify({"error": "Erro de integridade: verifique se o código de acesso já existe"}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500

@avaliacao.route('/avaliacao/acesso/<string:codigo>', methods=['GET'])
def buscar_por_codigo(codigo):
    try:
        # Busca a avaliação pelo código de acesso único
        prova = Avaliacao.get(Avaliacao.codigo_acesso == codigo)
        
        return jsonify({
            "id": prova.ID,
            "titulo": prova.titulo,
            "disciplina": prova.disciplina,
            "professor": prova.CPF_professor.nome_completo,
            "data_inicio": str(prova.data_inicio),
            "data_fim": str(prova.data_fim),
            "tempo_total": prova.tempo
        }), 200
        
    except Avaliacao.DoesNotExist:
        return jsonify({"error": "Código de acesso inválido ou avaliação não encontrada"}), 404


@avaliacao.route('/avaliacao', methods=['GET'])
def listar_avaliacoes():
    avaliacoes = Avaliacao.select()
    resultado = []
    
    for avaliacao in avaliacoes:
        resultado.append({
            "id": avaliacao.ID,
            "cpf_professor": avaliacao.CPF_professor_id, 
            "titulo": avaliacao.titulo,
            "tipo": avaliacao.tipo,
            "curso": avaliacao.curso,
            "turma": avaliacao.turma,
            "disciplina": avaliacao.disciplina,
            "data_inicio": str(avaliacao.data_inicio), # Converter data para texto
            "data_fim": str(avaliacao.data_fim),       # Converter data para texto
            "tempo": str(avaliacao.tempo),             # Converter tempo para texto
            "codigo_acesso": avaliacao.codigo_acesso
        })
        
    return jsonify(resultado), 200

@avaliacao.route('/avaliacao/<int:id>', methods=['GET'])
def buscar_avaliacao_por_id(id):
    try:
        avaliacao = Avaliacao.get(Avaliacao.ID == id)
        resultado = {
            "id": avaliacao.ID,
            "cpf_professor": avaliacao.CPF_professor_id,
            "titulo": avaliacao.titulo,
            "tipo": avaliacao.tipo,
            "curso": avaliacao.curso,
            "turma": avaliacao.turma,
            "disciplina": avaliacao.disciplina,
            "data_inicio": str(avaliacao.data_inicio),
            "data_fim": str(avaliacao.data_fim),
            "tempo": str(avaliacao.tempo),
            "codigo_acesso": avaliacao.codigo_acesso
        }
        return jsonify(resultado), 200
    except Avaliacao.DoesNotExist:
        return jsonify({"error": "Avaliação não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao buscar avaliação", "details": str(e)}), 500

@avaliacao.route('/avaliacao/<int:id>', methods=['PATCH'])
def atualizar_avaliacao(id):
    dados = request.get_json()
    
    try:
        avaliacao = Avaliacao.get(Avaliacao.ID == id)
        
        # Atualiza os campos fornecidos
        if 'cpf_professor' in dados:
            professor_existente = Professor.get_or_none(Professor.CPF == dados.get('cpf_professor'))
            if professor_existente is None:
                return jsonify({"error": "CPF do professor não encontrado no sistema"}), 400
            avaliacao.CPF_professor = dados.get('cpf_professor')
        
        if 'titulo' in dados:
            avaliacao.titulo = dados['titulo']
        if 'tipo' in dados:
            avaliacao.tipo = dados['tipo']
        if 'curso' in dados:
            avaliacao.curso = dados['curso']
        if 'turma' in dados:
            avaliacao.turma = dados['turma']
        if 'disciplina' in dados:
            avaliacao.disciplina = dados['disciplina']
        if 'data_inicio' in dados:
            avaliacao.data_inicio = dados['data_inicio']
        if 'data_fim' in dados:
            avaliacao.data_fim = dados['data_fim']
        if 'tempo' in dados:
            avaliacao.tempo = dados['tempo']
        if 'codigo_acesso' in dados:
            avaliacao.codigo_acesso = dados['codigo_acesso']
        
        avaliacao.save()
        return jsonify({"message": "Avaliação atualizada com sucesso!"}), 200
    except Avaliacao.DoesNotExist:
        return jsonify({"error": "Avaliação não encontrada"}), 404
    except IntegrityError:
        return jsonify({"error": "Erro de integridade: verifique os dados enviados"}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar avaliação", "details": str(e)}), 500



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



@avaliacao.route('/avaliacao/clonar/<int:id_original>', methods=['POST'])
def clonar_avaliacao(id_original):
    try:
        # 1. Busca a avaliação que será clonada
        original = Avaliacao.get_or_none(Avaliacao.ID == id_original)
        
        if not original:
            return jsonify({"error": "Avaliação original não encontrada"}), 404
        
        # 2. Obtém os dados extras do request (ex: um novo código de acesso)
        dados = request.get_json()
        novo_codigo = dados.get('novo_codigo_acesso')
        
        if not novo_codigo:
            return jsonify({"error": "É necessário fornecer um novo código de acesso único para o clone"}), 400

        # 3. Cria a nova avaliação baseada na original
        clone = Avaliacao.create(
            CPF_professor=original.CPF_professor, # Mantém o mesmo professor
            titulo=f"{original.titulo} (Cópia)",
            tipo=original.tipo,
            curso=original.curso,
            turma=original.turma,
            disciplina=original.disciplina,
            data_inicio=original.data_inicio,
            data_fim=original.data_fim,
            tempo=original.tempo,
            codigo_acesso=novo_codigo # Novo código obrigatório
        )
        
        return jsonify({
            "message": "Avaliação clonada com sucesso!",
            "novo_id": clone.ID,
            "novo_codigo": clone.codigo_acesso
        }), 201

    except IntegrityError:
        return jsonify({"error": "O novo código de acesso já está em uso"}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao clonar", "details": str(e)}), 500

@avaliacao.route('/avaliacao/iniciar', methods=['POST'])
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

@avaliacao.route('/avaliacao/responder-questao', methods=['POST'])
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

@avaliacao.route('/avaliacao/finalizar', methods=['POST'])
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