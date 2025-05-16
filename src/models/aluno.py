from src.models.db import db
from datetime import datetime

class Aluno(db.Model):
    __tablename__ = 'aluno'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='na_escola')  # na_escola, preparando, aguardando, entregue
    qrcode = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com responsáveis - definido após a criação da tabela de associação
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'turma': self.turma,
            'status': self.status,
            'qrcode': self.qrcode,
            'updated_at': self.updated_at.isoformat()
        }
