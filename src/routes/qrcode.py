from flask import Blueprint, request, jsonify, session
from src.models import db, Aluno, Responsavel
import qrcode
import os
import uuid
import base64
from io import BytesIO
from datetime import datetime

qrcode_bp = Blueprint('qrcode', __name__)

@qrcode_bp.route('/gerar/<int:aluno_id>', methods=['GET'])
def gerar_qrcode(aluno_id):
    if 'responsavel_id' not in session:
        return jsonify({'message': 'Não autorizado'}), 401
    
    responsavel_id = session['responsavel_id']
    responsavel = Responsavel.query.get(responsavel_id)
    
    if not responsavel:
        return jsonify({'message': 'Responsável não encontrado'}), 404
    
    aluno = Aluno.query.get(aluno_id)
    
    if not aluno or aluno not in responsavel.alunos:
        return jsonify({'message': 'Aluno não encontrado ou não associado a este responsável'}), 404
    
    # Se o aluno não tiver um QR code, gerar um novo
    if not aluno.qrcode:
        aluno.qrcode = f"aluno_{aluno.id}_{responsavel.id}_{uuid.uuid4().hex[:8]}"
        db.session.commit()
    
    # Gerar imagem do QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(aluno.qrcode)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({
        'qrcode': aluno.qrcode,
        'qrcode_image': f"data:image/png;base64,{img_str}"
    }), 200

@qrcode_bp.route('/verificar', methods=['POST'])
def verificar_qrcode():
    data = request.get_json()
    
    if not data or not data.get('qrcode'):
        return jsonify({'message': 'Dados incompletos'}), 400
    
    qrcode_valor = data.get('qrcode')
    aluno = Aluno.query.filter_by(qrcode=qrcode_valor).first()
    
    if not aluno:
        return jsonify({
            'valido': False,
            'message': 'QR Code inválido ou não reconhecido'
        }), 404
    
    # Verificar se o aluno está aguardando na portaria
    if aluno.status == 'aguardando':
        # Atualizar status para entregue
        aluno.status = 'entregue'
        aluno.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'valido': True,
            'message': f'QR Code válido! Aluno {aluno.nome} entregue ao responsável.',
            'aluno': aluno.to_dict()
        }), 200
    elif aluno.status == 'entregue':
        return jsonify({
            'valido': True,
            'message': f'Aluno {aluno.nome} já foi entregue ao responsável.',
            'aluno': aluno.to_dict()
        }), 200
    else:
        return jsonify({
            'valido': False,
            'message': f'QR Code válido para {aluno.nome}, mas o responsável ainda não chegou.',
            'aluno': aluno.to_dict()
        }), 400
