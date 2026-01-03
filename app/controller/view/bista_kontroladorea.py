from flask import flash, Blueprint, render_template, request, redirect, url_for
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
      try:
        taldea_id = service.sortu_taldea_hutsa('juan')  
        return redirect(url_for('taldeak.taldea', izena=taldea_id))

      except ValueError as e:
         flash(str(e), "error") # Enviamos el mensaje de error al HTML
         return redirect(url_for('taldeak.taldeak_kargatu'))
   
   @taldeak_bp.route('/kargatu_taldea', methods=['POST'])
   def kargatu_taldea():
      talde_izena = request.form.get('talde_izena')
      print(talde_izena)
      talde_datuak = service.get_taldea(talde_izena, 'juan')
      
      return render_template('taldea.html', pokemons=talde_datuak, izena=talde_izena)

   
   return taldeak_bp  # Ensure the Blueprint object is returned


def pokedex_blueprint(db):
   pokedex_bp = Blueprint('pokedex', __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   @pokedex_bp.route('/pokedex', methods=['GET', 'POST'])
   @pokedex_bp.route('/pokedex/bilatu', methods=['GET', 'POST'])
   def pokedex():
      iragazkiak = {'izena': None, 'generazioak': [], 'motak': []}
      if request.method == 'POST':
         izena = request.form.get('izena')
         if izena:
            iragazkiak['izena'] = izena
         generazioak = request.form.getlist('generazioak')
         if generazioak:
            iragazkiak['generazioak'] = generazioak
         motak = request.form.getlist('motak')
         if motak:
            iragazkiak['motak'] = motak
      pokemon_zerrenda = service.pokedex_kargatu(iragazkiak)
      return render_template('pokedex.html', pokemons=pokemon_zerrenda)
   @pokedex_bp.route('/pokedex/pokemon/<int:id>', methods=['GET'])
   def pokemon(id):
      datuak = service.bistaratu_pokemon(id)

      return render_template('pokemon.html', pokemon=datuak)
   return pokedex_bp