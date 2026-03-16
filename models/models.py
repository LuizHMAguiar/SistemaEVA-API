#models.py (COMPLETO E CORRIGIDO)
from peewee import *    
import datetime 
#Importações necessárias para login/segurança
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#Conexão com o banco de dados
db = SqliteDatabase("database.db")

class BaseModel(Model):
    class Meta:
        database = db 

# CRIAR CADA ENTIDADE BASEADO NO DIAGRAMA PARA UM BANCO DE DADOS 
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
    tempo = TimeField()

class Questao(BaseModel):  
    ID = AutoField(primary_key=True)
    tipo = CharField()
    enunciado = CharField()
    opcao_a= CharField()
    opcao_b= CharField()    
    opcao_c= CharField()
    opcao_d= CharField()
    opcao_e= CharField()

class QuestaoAvaliacao(BaseModel):
    ID_questao = ForeignKeyField(Questao)   
    ID_avaliacao = ForeignKeyField(Avaliacao)                                            
                   
    class Meta: 
        primary_key = CompositeKey('ID_questao', 'ID_avaliacao')

class RespostaAvaliacao(BaseModel):
    CPF_aluno = ForeignKeyField(Aluno)
    ID_avaliacao = ForeignKeyField(Avaliacao)

    class Meta:
        primary_key = CompositeKey('CPF_aluno', 'ID_avaliacao')
    
    data_hora_inicio = DateTimeField()
    data_hora_fim = DateTimeField()
    tempo_corrido = TimeField()
    
class RespostaQuestao(BaseModel):
    CPF_aluno = ForeignKeyField(Aluno)
    ID_avaliacao = ForeignKeyField(Avaliacao)
    ID_questao = ForeignKeyField(Questao)

    class Meta:
        primary_key = CompositeKey('CPF_aluno', 'ID_avaliacao', 'ID_questao') 
    
    resposta = CharField()
    audio_resposta = BlobField()

