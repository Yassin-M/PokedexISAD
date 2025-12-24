from flask import Blueprint, render_template, session
from app.controller import eredu_kontroladorea
class BistaKontroladorea:
   #metodos
   def __init__(self):
      pass

   @bista_bp.route('/changelog')
   def changelog():
    ErabiltzaileIzena = "Ash"

    lista_notificaciones = eredu_kontroladorea.notifikazioenInformazioaLortu(ErabiltzaileIzena)

    return render_template('changelog.html', notificaciones=lista_notificaciones)