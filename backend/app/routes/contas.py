from flask import Blueprint, jsonify, request
from ..models import Conta,CicloMes,Usuario, db
from flask_jwt_extended import jwt_required, get_jwt_identity


contas_bp = Blueprint('contas', __name__)

def aplicar_regras_negocio(conta, mes_atual=None):
    
    if mes_atual is None:
        ciclo_mes = CicloMes.query.filter_by(atual=True).first()
        
        if not ciclo_mes:
            raise Exception("Nenhum CicloMes ativo encontrado.")
        
    else:
        ciclo_mes = mes_atual
    
    conta.multiplicador = (conta.saldo_atual / ciclo_mes.investimento)

    conta.operacoes_finalizadas = ciclo_mes.alcancado

    conta.margem_lucro = conta.operacoes_finalizadas * (conta.multiplicador)

    conta.comissao_fundo = conta.margem_lucro * (conta.comissao)

    conta.liquido = conta.margem_lucro - conta.comissao_fundo
    
def atualizar_todas_contas(ciclo_mes):
    # Buscar todas as contas do sistema
    contas = Conta.query.all()

    # Recalcular as regras de negócio para cada conta usando a função importada
    for conta in contas:
        aplicar_regras_negocio(conta, ciclo_mes)

    # Commit das atualizações
    db.session.commit()


@contas_bp.route('/contas', methods=['POST'])
@jwt_required()
def criar_conta():
    
    usuario_logado_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_logado_id)
    
    if usuario.tipo_usuario != 'admin':
        return jsonify({'erro': 'Apenas usuarios permitidos podem criar contas'})
    
    
    dados = request.json

    # Validação básica dos campos obrigatórios
    if not dados.get('plano') or not dados.get('meses') or not dados.get('comissao') or not dados.get('nome') or not dados.get('usuario_id'):
        return jsonify({'erro': 'Necessário dados obrigatórios'}), 400
    
    try:
        nova_conta = Conta(
            usuario_id= dados['usuario_id'],
            nome = dados['nome'],
            deposito_inicial=dados['deposito_inicial'],
            saldo_atual=dados['saldo_atual'],
            plano=dados['plano'],
            meses=dados['meses'],
            comissao=dados['comissao']
        )
        
        aplicar_regras_negocio(nova_conta)

        db.session.add(nova_conta)
        db.session.commit()

        return jsonify({'message': 'Conta criada com sucesso', 'conta': nova_conta.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@contas_bp.route('/contas/user', methods=['GET'])
@jwt_required()
def listar_minhas_contas():
    
    usuario_id_logado = get_jwt_identity()
    
    contas = Conta.query.filter_by(usuario_id=usuario_id_logado).all()
    
    return jsonify([{
        'id': conta.id,
        'nome': conta.nome,
        'usuario_id': conta.usuario_id,
        'deposito_inicial': conta.deposito_inicial,
        'saldo_atual': conta.saldo_atual,
        'multiplicador': conta.multiplicador,
        'plano': conta.plano,
        'meses': conta.meses,
        'liquido': conta.liquido,
        'comissao': conta.comissao,
        'operacoes_finalizadas': conta.operacoes_finalizadas,
        'margem_lucro': conta.margem_lucro,
        'comissao_fundo': conta.comissao_fundo,
        'inicio': conta.inicio,
        'saques': conta.saques
    } for conta in contas]), 200
    
@contas_bp.route('/contas/user/<int:id>', methods=['GET'])
@jwt_required()
def listar_contas_usuario(id):
    
    usuario_id_logado = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id_logado)
    
    if usuario.tipo_usuario != 'admin':
        return jsonify({'erro': 'Apenas usuarios permitidos podem acessar todas as contas'})
    
    contas = Conta.query.filter_by(usuario_id=id).all()
    
    return jsonify([{
        'id': conta.id,
        'nome': conta.nome,
        'usuario_id': conta.usuario_id,
        'deposito_inicial': conta.deposito_inicial,
        'saldo_atual': conta.saldo_atual,
        'multiplicador': conta.multiplicador,
        'plano': conta.plano,
        'meses': conta.meses,
        'liquido': conta.liquido,
        'comissao': conta.comissao,
        'operacoes_finalizadas': conta.operacoes_finalizadas,
        'margem_lucro': conta.margem_lucro,
        'comissao_fundo': conta.comissao_fundo,
        'inicio': conta.inicio,
        'saques': conta.saques
    } for conta in contas]), 200
    
@contas_bp.route('/contas', methods=['GET'])
@jwt_required()
def get_all_contas(): 
    contas = Conta.query.all()
    
    return jsonify([{
        'id': conta.id,
        'nome': conta.nome,
        'usuario_id': conta.usuario_id,
        'deposito_inicial': conta.deposito_inicial,
        'saldo_atual': conta.saldo_atual,
        'multiplicador': conta.multiplicador,
        'plano': conta.plano,
        'meses': conta.meses,
        'liquido': conta.liquido,
        'comissao': conta.comissao,
        'operacoes_finalizadas': conta.operacoes_finalizadas,
        'margem_lucro': conta.margem_lucro,
        'comissao_fundo': conta.comissao_fundo,
        'inicio': conta.inicio,
        'saques': conta.saques
    } for conta in contas]), 200
    
@contas_bp.route('/contas/<int:id>', methods=['GET'])
@jwt_required()
def get_conta(id):
    usuario_id_logado = get_jwt_identity()
    
    conta = Conta.query.get_or_404(id)
    
    if conta.usuario_id != usuario_id_logado:
        return jsonify({'erro': 'Você não tem permissão para acessar esta conta'}), 403
    
    return jsonify([{
        'id': conta.id,
        'nome': conta.nome,
        'usuario_id': conta.usuario_id,
        'deposito_inicial': conta.deposito_inicial,
        'saldo_atual': conta.saldo_atual,
        'multiplicador': conta.multiplicador,
        'plano': conta.plano,
        'meses': conta.meses,
        'liquido': conta.liquido,
        'comissao': conta.comissao,
        'operacoes_finalizadas': conta.operacoes_finalizadas,
        'margem_lucro': conta.margem_lucro,
        'comissao_fundo': conta.comissao_fundo,
        'inicio': conta.inicio,
        'saques': conta.saques
    }])


@contas_bp.route('/contas/<int:id>', methods=['PUT'])
@jwt_required()
def editar_conta(id):
    dados = request.json
    
    usuario_logado_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_logado_id)
    
    if usuario.tipo_usuario != 'admin':
        return jsonify({'erro': 'Apenas usuarios permitidos podem editar contas'})
    

    
    conta = Conta.query.get_or_404(id)

    try:
        if 'deposito_inicial' in dados:
            conta.deposito_inicial = dados['deposito_inicial']
        if 'saldo_atual' in dados:
            conta.saldo_atual = dados['saldo_atual']
        if 'plano' in dados:
            conta.plano = dados['plano']
        if 'meses' in dados:
            conta.meses = dados['meses']
        if 'comissao' in dados:
            conta.comissao = dados['comissao']
        if 'saques' in dados:
            conta.saques = dados['saques']
        if 'nome' in dados:
            conta.nome = dados['nome']
      
        aplicar_regras_negocio(conta)
        db.session.commit()
        return jsonify({'message': 'Conta atualizada com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500


@contas_bp.route('/contas/<int:id>', methods=['DELETE'])
@jwt_required()
def excluir_conta(id):
    
    usuario_logado_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_logado_id)

    
    if usuario.tipo_usuario != 'admin':
        return jsonify({'erro': 'Apenas usuarios permitidos podem excluir contas'})
    
    conta = Conta.query.get_or_404(id)
    
    try:
        db.session.delete(conta)
        db.session.commit()
        return jsonify({'message': 'Conta excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
    
    
