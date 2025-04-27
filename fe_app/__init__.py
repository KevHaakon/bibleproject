# fe_app/__init__.py

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_cors import CORS
import os
from datetime import datetime

from config import config_by_name 

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
         config_name = os.environ.get('FLASK_ENV', 'dev')

    app.config.from_object(config_by_name[config_name])

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    CORS(app) 

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    from . import models
    from .auth import auth
    from .bible import bible_bp
    from .ai import ai_bp

    app.register_blueprint(auth)
    app.register_blueprint(bible_bp) 
    app.register_blueprint(ai_bp)
 
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    @app.route('/')
    def serve_index():
        if current_user.is_authenticated:
            current_year = datetime.now().year
            print("Usuario autenticado. Sirviendo index.html.")
            return render_template('index.html', current_year=current_year)
        else:
            print("Usuario no autenticado. Redirigiendo a login.")
            return redirect(url_for('auth.login'))

    return app
