from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, Responsavel, Aluno
import uuid
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    responsavel = Responsavel.query.filter_by(email=data.get('email')).first()
    
    if not responsavel or not responsavel.verificar_senha(data.get('senha')):
        return jsonify({'message': 'Email ou senha incorretos'}), 401
    
    session['responsavel_id'] = responsavel.id
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'responsavel': responsavel.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('responsavel_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    
    if not data or not data.get('nome') or not data.get('email') or not data.get('senha') or not data.get('telefone'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    if Responsavel.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email já cadastrado'}), 400
    
    novo_responsavel = Responsavel(
        nome=data.get('nome'),
        email=data.get('email'),
        telefone=data.get('telefone')
    )
    novo_responsavel.set_senha(data.get('senha'))
    
    db.session.add(novo_responsavel)
    db.session.commit()
    
    return jsonify({
        'message': 'Cadastro realizado com sucesso',
        'responsavel': novo_responsavel.to_dict()
    }), 201
