from . import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)
    authenticator_secret = db.Column(db.String(100), nullable=True)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    deposito_inicial = db.Column(db.Float, nullable=False)
    saldo_atual = db.Column(db.Float, nullable=False)
    multiplicador = db.Column(db.Float, nullable=False)
    plano = db.Column(db.String(100), nullable=False)
    meses = db.Column(db.String(50), nullable=False)
    liquido = db.Column(db.Float, nullable=False)
    comissao = db.Column(db.Float, nullable=False)
    operacoes_finalizadas = db.Column(db.Float, nullable=False)
    margem_lucro = db.Column(db.Float, nullable=False)
    comissao_fundo = db.Column(db.Float, nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    saques = db.Column(db.Float, nullable=False)
    

class CicloMes(db.Model):
    __tablename__ = 'ciclomes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable = False)
    investimento = db.Column(db.Float, nullable=False)
    dias = db.Column(db.Integer, nullable=False)
    shark = db.Column(db.Float, nullable=False)
    alcancado = db.Column(db.Float, nullable=False)
    projecao = db.Column(db.Float, nullable=False)
    porcentagem_alcancado = db.Column(db.Float, nullable=False)
    valor_liquido = db.Column(db.Float, nullable=False)
    atual = db.Column(db.Boolean, nullable=False, default=False)

class Dia(db.Model):
    __tablename__ = 'dias'
    id = db.Column(db.Integer, primary_key=True)
    mes_id = db.Column(db.Integer, db.ForeignKey('ciclomes.id'), nullable=False)
    saldo_inicial = db.Column(db.Float, nullable=False)
    juros = db.Column(db.Float, nullable=False)
    alcancado_dia = db.Column(db.Float, nullable=False)
