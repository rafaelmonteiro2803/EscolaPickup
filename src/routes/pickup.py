from flask import Blueprint, request, jsonify, session
from src.models import db, Responsavel, Aluno
import qrcode
import os
import uuid
from datetime import datetime

pickup_bp = Blueprint('pickup', __name__)

@pickup_bp.route('/status', methods=['POST'])
def atualizar_status():
    data = request.get_json()
    
    if 'responsavel_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    
    responsavel_id = session['responsavel_id']
    responsavel = Responsavel.query.get(responsavel_id)
    
    if not responsavel:
        return jsonify({'message': 'Responsável não encontrado'}), 404
    
    novo_status = data.get('status')
    if novo_status not in ['inativo', 'a_caminho', 'chegou']:
        return jsonify({'message': 'Status inválido'}), 400
    
    responsavel.status = novo_status
    responsavel.updated_at = datetime.utcnow()
    
    # Se o responsável chegou, atualizar status dos alunos para "preparando"
    if novo_status == 'a_caminho':
        for aluno in responsavel.alunos:
            if aluno.status == 'na_escola':
                aluno.status = 'preparando'
                aluno.updated_at = datetime.utcnow()
    
    # Se o responsável chegou, atualizar status dos alunos para "aguardando"
    if novo_status == 'chegou':
        for aluno in responsavel.alunos:
            if aluno.status in ['na_escola', 'preparando']:
                aluno.status = 'aguardando'
                aluno.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Status atualizado com sucesso',
        'responsavel': responsavel.to_dict(),
        'alunos': [aluno.to_dict() for aluno in responsavel.alunos]
    }), 200

@pickup_bp.route('/alunos', methods=['GET'])
def listar_alunos():
    if 'responsavel_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    
    responsavel_id = session['responsavel_id']
    responsavel = Responsavel.query.get(responsavel_id)
    
    if not responsavel:
        return jsonify({'message': 'Responsável não encontrado'}), 404
    
    return jsonify({
        'alunos': [aluno.to_dict() for aluno in responsavel.alunos]
    }), 200

@pickup_bp.route('/qrcode/<int:aluno_id>', methods=['GET'])
def obter_qrcode(aluno_id):
    if 'responsavel_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    
    responsavel_id = session['responsavel_id']
    responsavel = Responsavel.query.get(responsavel_id)
    
    if not responsavel:
        return jsonify({'message': 'Responsável não encontrado'}), 404
    
    aluno = Aluno.query.get(aluno_id)
    
    if not aluno or aluno not in responsavel.alunos:
        return jsonify({'message': 'Aluno não encontrado ou não associado a este responsável'}), 404
    
    return jsonify({
        'qrcode': aluno.qrcode
    }), 200
