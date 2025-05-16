from src.models.db import db
from datetime import datetime
from src.models.aluno import Aluno
from src.models.responsavel import Responsavel

# Tabela de associação entre alunos e responsáveis
aluno_responsavel = db.Table('aluno_responsavel',
    db.Column('aluno_id', db.Integer, db.ForeignKey('aluno.id'), primary_key=True),
    db.Column('responsavel_id', db.Integer, db.ForeignKey('responsavel.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# Definir relacionamentos após a criação da tabela de associação
Aluno.responsaveis = db.relationship('Responsavel', secondary=aluno_responsavel, back_populates='alunos')
Responsavel.alunos = db.relationship('Aluno', secondary=aluno_responsavel, back_populates='responsaveis')
