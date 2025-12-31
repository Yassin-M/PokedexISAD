from flask import Blueprint, render_template, request, redirect, url_for
from app.controller.model.eredu_kontroladorea import EreduKontroladorea


def taldeak_blueprint(db):
   taldeak_bp = Blueprint('taldeak', __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   talde_zerrenda = service.taldeak_kargatu('juan')
   print("Loaded taldeak:", talde_zerrenda)  # Debugging output

   @taldeak_bp.route('/taldeak', methods=['GET', 'POST'])
   def taldeak_kargatu():
      talde_zerrenda = service.taldeak_kargatu('juan')
      return render_template('taldeak.html', taldeak=talde_zerrenda)

   @taldeak_bp.route('/taldea/<string:izena>')
   def taldea(izena):
      taldea = service.get_taldea(izena, 'juan')
      return render_template('taldea.html', taldea=taldea)

   @taldeak_bp.route('/taldea', methods=['POST'])
   def sortu_taldea():
      taldea_id = service.sortu_taldea_hutsa('juan')
      return redirect(url_for('taldeak.taldea', izena=taldea_id))



   return taldeak_bp  # Ensure the Blueprint object is returned

