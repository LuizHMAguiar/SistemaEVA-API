from peewee import *
import datetime

db = SqliteDatabase("database.db")

class BaseModel(Model):
    class Meta:
        database = db 

class Instituicao(BaseModel):
    CNPJ = CharField(primary_key=True)
    nome = CharField()
    email = CharField()
    senha = CharField()

class Professor(BaseModel):
    CPF = CharField(primary_key=True)
    CNPJ_instituicao = ForeignKeyField(Instituicao)
    nome_completo = CharField()
    email = CharField()
    senha = CharField()

class Aluno(BaseModel):
    CPF = CharField(primary_key=True)
    CNPJ_instituicao = ForeignKeyField(Instituicao)
    nome_completo = CharField()
    email = CharField()
    senha = CharField()
    curso = CharField()
    turma = CharField()

class Avaliacao(BaseModel):
    ID = AutoField(primary_key=True)
    CPF_professor = ForeignKeyField(Professor)
    titulo = CharField()
    tipo = CharField()
    curso = CharField()
    turma = CharField()
    disciplina = CharField()
    data_inicio = DateTimeField()
    data_fim = DateTimeField()
    tempo = CharField() # Alterado para CharField para aceitar formatos como "02:00"
    codigo_acesso = CharField(unique=True, null=True) # CAMPO ADICIONADO

class Questao(BaseModel):  
    ID = AutoField(primary_key=True)
    CPF_professor = ForeignKeyField(Professor)
    tipo = CharField()
    enunciado = CharField()
    opcao_a = CharField()
    opcao_b = CharField()    
    opcao_c = CharField(null=True) 
    opcao_d = CharField(null=True) 
    opcao_e = CharField(null=True) 

class QuestaoAvaliacao(BaseModel):
    ID_questao = ForeignKeyField(Questao)   
    ID_avaliacao = ForeignKeyField(Avaliacao)                                            
                   
    class Meta: 
        primary_key = CompositeKey('ID_questao', 'ID_avaliacao')

class RespostaAvaliacao(BaseModel):
    CPF_aluno = ForeignKeyField(Aluno)
    ID_avaliacao = ForeignKeyField(Avaliacao)
    data_hora_inicio = DateTimeField()
    data_hora_fim = DateTimeField(null=True)
    tempo_corrido = CharField(null=True)

    class Meta:
        primary_key = CompositeKey('CPF_aluno', 'ID_avaliacao')
    
class RespostaQuestao(BaseModel):
    CPF_aluno = ForeignKeyField(Aluno)
    ID_avaliacao = ForeignKeyField(Avaliacao)
    ID_questao = ForeignKeyField(Questao)
    resposta = TextField(null=True)
    audio_resposta = BlobField(null=True)

    class Meta:
        primary_key = CompositeKey('CPF_aluno', 'ID_avaliacao', 'ID_questao')