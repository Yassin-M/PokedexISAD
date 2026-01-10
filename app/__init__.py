import os.path
import sqlite3
from flask import Flask
from app.database.database import Connection
from app.controller.view.bista_kontroladorea import pokedex_blueprint
from app.controller.view.bista_kontroladorea import itemdex_blueprint
from app.controller.view.bista_kontroladorea import chatbot_blueprint
from app.controller.view.bista_kontroladorea import bista_blueprint
from app.controller.view.bista_kontroladorea import taldeak_blueprint

from flask import Flask, render_template, redirect, url_for, session, request, flash

from app.database.database import Connection
from app.controller.view.bista_kontroladorea import BistaKontroladorea


def create_app():
    app = Flask(__name__)
    app.secret_key = 'claveultrasupermegasecreta'
    
    # Inicializar la DB primero
    db = Connection()
    
    vista_controller = BistaKontroladorea(db)

    # Registrar blueprint de Itemdex
    app.register_blueprint(itemdex_blueprint(db))
    app.register_blueprint(pokedex_blueprint(db))
    app.register_blueprint(chatbot_blueprint(db))
    app.register_blueprint(taldeak_blueprint(db))
    app.register_blueprint(bista_blueprint(db))

    
    
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        erabiltzailea = request.form.get('erabiltzailea') if request.method == 'POST' else None
        pasahitza = request.form.get('password') if request.method == 'POST' else None
        return vista_controller.saioHasi(erabiltzailea, pasahitza)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        return vista_controller.erregistratu()

    @app.route('/editatu', methods=['GET', 'POST'])
    def editatu():
        return vista_controller.datuakAldatu()

    @app.route('/menu')
    def menu():
        return render_template('menu.html')
    
    @app.route('/menu_admin')
    def menu_admin():
        return render_template('menu_admin.html')

    @app.route('/kudeatu')
    def kudeatu():
        return vista_controller.erabiltzaileakKargatu()
    
    @app.route('/kudeatu/editatu/<user_id>', methods=['GET', 'POST'])
    def editatu_user(user_id):
        return vista_controller.datuakAldatu(user_id)

    @app.route('/kudeatu/ezabatu/<user_id>')
    def delete_user(user_id):
        return vista_controller.ezabatu(user_id)

    @app.route('/kudeatu/admin/<user_id>')
    def make_admin(user_id):
        return vista_controller.baimendu(user_id)
    
    @app.route('/lagunak')
    def lagunak():
        return vista_controller.lagunakKargatu()

    @app.route('/lagunak/notifikazioak/<jarraitua>')
    def eguneratu_notifikazioak(jarraitua):
        return vista_controller.eguneratu_notifikazioak(jarraitua)

    @app.route('/lagunak/utzi/<jarraitua>')
    def utzi_jarraitzen(jarraitua):
        return vista_controller.utzi_jarraitzen(jarraitua)

    @app.route('/gehituErabiltzailea')
    @app.route('/gehituErabiltzailea/<jarraitua>')
    def gehituErabiltzailea(jarraitua=None):
        return vista_controller.gehituErabiltzailea(jarraitua)
    

    return app