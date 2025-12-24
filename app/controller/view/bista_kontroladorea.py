from flask import Blueprint, render_template, session
from app.controller.model import eredu_kontroladorea
bista_bp = Blueprint('bista_orokorra', __name__)
   #metodos
def __init__(self):
      pass

@bista_bp.route('/changelog')
def changelog():
    ErabiltzaileIzena = session.get('erabiltzaile_izena')

    lista_notificaciones = eredu_kontroladorea.notifikazioenInformazioaLortu(ErabiltzaileIzena)

    return render_template('changelog.html', notificaciones=lista_notificaciones)