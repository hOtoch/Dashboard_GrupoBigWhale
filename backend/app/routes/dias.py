from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from ..models import Dia, Usuario,CicloMes, db
from ..routes.ciclomes import atualizar_ciclomes
from ..routes.contas import atualizar_todas_contas

dias_bp = Blueprint('dias', __name__)


@dias_bp.route('/dias/<int:id>', methods=['PUT'])
@jwt_required()  
def editar_dia(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.tipo_usuario != 'admin':
        return jsonify({'erro': 'Você não tem permissão para editar este Dia'}), 403

    dia = Dia.query.get_or_404(id)
    dados = request.json

    
    if 'mes_id' in dados:
        dia.mes_id = dados['mes_id']
   
    if 'alcancado_dia' in dados:
        dia.alcancado_dia = dados['alcancado_dia']
        
    atualizar_ciclomes(dia.mes_id)
    ciclomes = CicloMes.query.get_or_404(dia.mes_id)
    atualizar_todas_contas(ciclomes)

    try:
        db.session.commit()
        return jsonify({'message': 'Dia atualizado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@dias_bp.route('/dias/<int:id>', methods=['GET'])
@jwt_required()  
def acessar_dias_mes(id):
    
    try:
        dias = Dia.query.filter_by(mes_id=id).all()
        
        dias_lista = [{
            'id': dia.id,
            'mes_id': dia.mes_id,
            'juros': dia.juros,
            'alcancado_dia': dia.alcancado_dia
        } for dia in dias]

        return jsonify(dias_lista), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

