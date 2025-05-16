import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from src.models.db import db
from src.routes.auth import auth_bp
from src.routes.pickup import pickup_bp
from src.routes.user import user_bp
from src.routes.qrcode import qrcode_bp
import secrets

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(pickup_bp, url_prefix='/api/pickup')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(qrcode_bp, url_prefix='/api/qrcode')

# Habilitar banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/kanban')
def serve_kanban():
    kanban_path = os.path.join(app.static_folder, 'kanban.html')
    if os.path.exists(kanban_path):
        return send_from_directory(app.static_folder, 'kanban.html')
    else:
        return "kanban.html not found", 404

# Criar tabelas do banco de dados e dados iniciais
with app.app_context():
    db.create_all()
    
    # Verificar se já existem dados
    from src.models.aluno import Aluno
    from src.models.responsavel import Responsavel
    from src.models import aluno_responsavel
    
    if Responsavel.query.count() == 0:
        # Criar responsáveis
        rafael = Responsavel(nome='Rafael', email='rafael@exemplo.com', telefone='11999991111', status='inativo')
        rafael.set_senha('123456')
        
        chines = Responsavel(nome='Chines', email='chines@exemplo.com', telefone='11999992222', status='inativo')
        chines.set_senha('123456')
        
        juliana = Responsavel(nome='Juliana', email='juliana@exemplo.com', telefone='11999993333', status='inativo')
        juliana.set_senha('123456')
        
        # Criar alunos
        joao = Aluno(nome='João', turma='5º Ano - Manhã', status='na_escola', qrcode='aluno_1_rafael')
        bruno = Aluno(nome='Bruno', turma='3º Ano - Tarde', status='na_escola', qrcode='aluno_2_chines')
        olivia = Aluno(nome='Olivia', turma='1º Ano - Manhã', status='na_escola', qrcode='aluno_3_juliana')
        
        # Adicionar ao banco de dados
        db.session.add_all([rafael, chines, juliana, joao, bruno, olivia])
        db.session.commit()
        
        # Associar alunos aos responsáveis
        rafael.alunos.append(joao)
        chines.alunos.append(bruno)
        juliana.alunos.append(olivia)
        
        # Salvar associações
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
