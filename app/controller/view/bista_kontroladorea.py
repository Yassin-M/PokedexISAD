from flask import Blueprint, render_template, request, session
from app.controller.model import eredu_kontroladorea
bista_bp = Blueprint('bista_orokorra', __name__)

@bista_bp.route('/changelog')
def changelog():
    ErabiltzaileIzena = 'Ash'

    bilatutakoIzena = request.args.get('bilatutako_erabiltzaile_izena')

    lista_notificaciones = eredu_kontroladorea.notifikazioenInformazioaLortu(ErabiltzaileIzena, bilatutakoIzena)

    return render_template('changelog.html', notificaciones=lista_notificaciones)