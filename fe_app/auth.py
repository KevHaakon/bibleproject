# fe_app/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('serve_index'))

    current_year = datetime.now().year

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth_str = request.form.get('date_of_birth')
        country = request.form.get('country')

        if not username or not password or not email or not first_name or not last_name or not country:
            print("Intento de registro fallido: faltan campos requeridos")
            return jsonify({"status": "error", "message": "Campos obligatorios incompletos."}), 400

        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            print(f"Intento de registro fallido: Username '{username}' ya existe")
            return jsonify({"status": "error", "message": "El nombre de usuario ya está en uso."}), 409

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
             print(f"Intento de registro fallido: Email '{email}' ya existe")
             return jsonify({"status": "error", "message": "El correo electrónico ya está en uso."}), 409

        date_of_birth_obj = None
        if date_of_birth_str:
            try:
                date_of_birth_obj = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                 print(f"Intento de registro fallido: Formato de fecha inválido: {date_of_birth_str}")
                 return jsonify({"status": "error", "message": "Formato de fecha de nacimiento inválido (AAAA-MM-DD)."}, 400)

        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth_obj,
            country=country
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        print(f"Usuario '{username}' registrado exitosamente.")
        return jsonify({"status": "success", "message": "Usuario registrado exitosamente. Ahora puedes iniciar sesión."}), 201

    else:
        print("Sirviendo template de registro.")
        return render_template('register.html', current_year=current_year)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('serve_index'))

    current_year = datetime.now().year

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            print(f"Intento de login fallido: Credenciales inválidas para username '{username}'")
            return jsonify({"status": "error", "message": "Nombre de usuario o contraseña incorrectos."}), 401

        login_user(user)

        print(f"Usuario '{username}' ha iniciado sesión exitosamente.")
        next_page = request.args.get('next')
        return redirect(next_page or url_for('serve_index'))

    else:
        print("Sirviendo template de login.")
        return render_template('login.html', current_year=current_year)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    print("Usuario ha cerrado sesión.")
    return redirect(url_for('.login'))