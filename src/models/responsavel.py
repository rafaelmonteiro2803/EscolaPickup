from src.models.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Responsavel(db.Model):
    __tablename__ = 'responsavel'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='inativo')  # inativo, a_caminho, chegou
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com alunos - definido após a criação da tabela de associação
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Responsavel {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'status': self.status,
            'alunos': [aluno.nome for aluno in self.alunos] if hasattr(self, 'alunos') else []
        }
