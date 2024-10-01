from flask import Blueprint, request, jsonify, make_response, Flask,url_for,session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, decode_token
from ..models import Usuario, db
from flask_mail import Message
from datetime import timedelta
from .. import mail
from flask import current_app as app
import os


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



@login_bp.route('/login/google', methods=['GET'])
def login_google():
    nonce = os.urandom(16).hex()
    session['nonce'] = nonce
    return app.extensions['authlib.integrations.flask_client'].google.authorize_redirect("http://localhost:5000/auth/callback", nonce=nonce)


@login_bp.route('/auth/callback')
def authorize():
    nonce = session.pop('nonce', None)
    if not nonce:
        return jsonify({'erro': 'Nonce não encontrado'}), 400
    
    token = app.extensions['authlib.integrations.flask_client'].google.authorize_access_token()
    user_info = app.extensions['authlib.integrations.flask_client'].google.parse_id_token(token, nonce=nonce, claims_options={"iat": {"leeway": 60}})
    user = Usuario.query.filter_by(email=user_info['email']).first()
    if not user:
        user = Usuario(nome=user_info['name'], email=user_info['email'])
        db.session.add(user)
        db.session.commit()
    access_token = create_access_token(identity=user.id)
    return redirect(f"http://localhost:8501?token={access_token}")

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



    

    
    
