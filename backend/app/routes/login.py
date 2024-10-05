from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, decode_token
from ..models import Usuario, db
from flask_mail import Message
from datetime import timedelta
from io import BytesIO
import pyotp
import qrcode
import base64
from .. import mail


def send_reset_email(to, reset_link):
    msg = Message('ROI Investimentos - Instruções para Recuperação de Senha',
                  recipients=[to],
                  body=f'''Olá,

Recebemos uma solicitação para redefinir a senha associada à sua conta na ROI Investimentos.

Para criar uma nova senha, por favor, clique no link abaixo:

{reset_link}

Este link estará disponível por 24 horas. Se você não solicitou a recuperação de senha, pode ignorar esta mensagem com segurança.

Caso tenha qualquer dúvida, nossa equipe de suporte está à disposição para ajudá-lo.

Atenciosamente,
Equipe ROI Investimentos''',
                  sender='otochdev@gmail.com')
    mail.send(msg)
    

login_bp = Blueprint('login',__name__)


@login_bp.route('/login', methods =['POST'])
def login():
    dados = request.get_json()

    if not dados.get('email') or not dados.get('senha'):
        return jsonify({'erro':'Email e senha são obrigatórios'}),400
    
    user = Usuario.query.filter_by(email = dados.get('email')).first();
        
    if user and check_password_hash(user.senha_hash, dados.get('senha')):
        # gerar um token de acesso JWT com o ID do usuario
        access_token = create_access_token(identity=user.id)
        response = make_response(jsonify({
            'message': 'Login bem-sucedido',
            'access_token': access_token
        }))
        
        return response
    
    else:
        return jsonify({'erro':'Credenciais inválidas'}), 401
    

@login_bp.route('/verify_email', methods =['POST'])    
def verify_email():
    dados = request.get_json()
    
    user = Usuario.query.filter_by(email = dados.get('email')).first();
    
    if user:
        return jsonify({'message':'Email encontrado'}), 200
    else:
        return jsonify({'erro':'Email não encontrado'}), 404
    
@login_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    dados = request.get_json()

    # Verifique se o email foi enviado
    if not dados.get('email'):
        return jsonify({'erro': 'Email é obrigatório'}), 400

    # Verifique se o usuário existe
    user = Usuario.query.filter_by(email=dados.get('email')).first()

    if user:
        # Gera o token de redefinição de senha (JWT válido por 1 hora)
        reset_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))

        frontend_url = "http://localhost:4200/resetar-senha"  
        reset_url = f"{frontend_url}/{reset_token}"

        # Envia o email com o link de redefinição
        send_reset_email(user.email, reset_url)

        return jsonify({'message': 'Um email foi enviado com instruções para redefinir sua senha.'}), 200
    else:
        return jsonify({'erro': 'Email não encontrado'}), 404
    
@login_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Decodificar o token para obter o ID do usuário
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']  # 'sub' é o campo que contém o ID do usuário no JWT
    except:
        return jsonify({'erro': 'Token inválido ou expirado'}), 400

    if request.method == 'POST':
        dados = request.get_json()

        # Verifique se a nova senha foi enviada
        if not dados.get('new_password'):
            return jsonify({'erro': 'Nova senha é obrigatória'}), 400

        # Atualize a senha do usuário no banco de dados
        user = Usuario.query.get(user_id)
        user.senha_hash = generate_password_hash(dados.get('new_password'))
        db.session.commit()

        return jsonify({'message': 'Senha redefinida com sucesso!'}), 200

    # Se for uma requisição GET, você pode retornar uma mensagem ou renderizar um formulário (caso queira exibir uma página)
    return jsonify({'message': 'Insira sua nova senha.'}), 200

@login_bp.route('/authenticator/setup', methods=['POST'])
def setup():
    email = request.json.get('email')
    
    user = Usuario.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'erro':'Usuário não encontrado'}),404
    
    if user.authenticated:
        return jsonify({'message':'Authenticator já configurado'}),200
    
    # cria um segredo unico
    secret = pyotp.random_base32()
    
    user.authenticator_secret = secret
    
    totp = pyotp.TOTP(secret)
    
    # cria a URL para ser autenticada no Google Authenticator
    otp_uri = totp.provisioning_uri(name=email, issuer_name='ROI Investimentos')
    
    qr_code = qrcode.make(otp_uri)
    buffered = BytesIO()
    qr_code.save(buffered, format='PNG')
    
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    db.session.commit()
  
    
    return jsonify({
        'secret': secret,
        'qr_code': qr_code_base64,
        'message':f'QR Code gerado para o usuário {email}'
    }), 200
    
@login_bp.route('/authenticator/verify', methods=['POST'])
def verify():
    email = request.json.get('email')
    user_code = request.json.get('user_code')
    
    user = Usuario.query.filter_by(email=email).first()
    
    secret = user.authenticator_secret 
    
    totp = pyotp.TOTP(secret)
    
    print(totp.now())
    print(user_code)
    
    
    if totp.verify(user_code):
        user.authenticated = True
        db.session.commit()
        return jsonify({'message':'Código válido, login bem-sucedido!'}), 200
    else:
        return jsonify({'erro':'Código inválido'}), 400



    

    
    
