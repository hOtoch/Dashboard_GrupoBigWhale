from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
mail = Mail()

# Inicializar SQLAlchemy
db = SQLAlchemy()

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}
    )
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Configurar o banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
      
    expiration = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=expiration)

    # Inicializar a conexão com o banco de dados
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    from .routes import register_blueprints
    register_blueprints(app)

    return app
