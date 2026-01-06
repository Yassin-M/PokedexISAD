from flask import flash, Blueprint, render_template, request, redirect, session, url_for
from app.controller.model.eredu_kontroladorea import EreduKontroladorea
import datetime

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
        session['editatzen_ari_den_taldea'] = taldea_id
        deskripzioa = f"Talde berria sortu du: {taldea_id}."
        service.notifikazioBerria('juan', deskripzioa, datetime.datetime.now())

        return redirect(url_for('taldeak.taldea', izena=taldea_id))

      except ValueError as e:
         flash(str(e), "error") # Enviamos el mensaje de error al HTML
         return redirect(url_for('taldeak.taldeak_kargatu'))
   
   @taldeak_bp.route('/editatu_taldea', methods=['GET', 'POST'])
   def kargatu_taldea():
      
      if request.form.get('talde_izena'):
         talde_izena = request.form.get('talde_izena')
         session['editatzen_ari_den_taldea'] = talde_izena
      else:
         talde_izena = session.get('editatzen_ari_den_taldea')
      talde_datuak = service.get_taldea(talde_izena, 'juan')
      return render_template('taldea.html', pokemons=talde_datuak, izena=talde_izena)
   
   @taldeak_bp.route('/pokemon_taldea', methods=['POST'])
   def sartu_taldera():
      talde_izena = session.get('editatzen_ari_den_taldea')
      pokemon_id = session.get('pokemon_datuak')
      try:
         pokeIzena = service.sartu_taldera(talde_izena, 'juan', pokemon_id)
         service.notifikazioBerria('juan', f"{pokeIzena} bat gehitu du {talde_izena} taldean.", datetime.datetime.now())
         return redirect(url_for('taldeak.kargatu_taldea'))
      except ValueError as e:
         flash(str(e), "error")
         return redirect(url_for('taldeak.kargatu_taldea'))
   
   @taldeak_bp.route('/pokemon_taldea/ezabatu', methods=['GET', 'POST'])
   def ezabatu_taldetik():
      talde_izena = session.get('editatzen_ari_den_taldea')
      pokemon_id = session.get('pokemon_datuak')
      pokeIzena = service.ezabatu_taldetik(talde_izena, 'juan', pokemon_id)
      service.notifikazioBerria('juan', f"{pokeIzena} bat ezabatu du {talde_izena} taldean.", datetime.datetime.now())

      akzioa = request.args.get('akzioa')
      if akzioa == 'hauta_pokemon':
         session['akzioa'] = 'hauta_pokemon'
         print(session['akzioa'])
         return redirect(url_for('pokedex.pokedex'))
      else:
         return redirect(url_for('taldeak.kargatu_taldea'))

   @taldeak_bp.route('/taldea/ezabatu', methods=['GET', 'POST'])
   def taldea_ezabatu():
      talde_izena = session.get('editatzen_ari_den_taldea')
      service.ezabatu_taldea(talde_izena, 'juan')
      service.notifikazioBerria('juan', f"{talde_izena} taldea ezabatu du.", datetime.datetime.now())
      return redirect(url_for('taldeak.taldeak_kargatu'))
   
   return taldeak_bp  # Ensure the Blueprint object is returned


def pokedex_blueprint(db):
   pokedex_bp = Blueprint('pokedex', __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   @pokedex_bp.route('/pokedex', methods=['GET', 'POST'])
   @pokedex_bp.route('/pokedex/bilatu', methods=['GET', 'POST'])
   def pokedex():
      
      if request.form.get('akzioa') is not None:
         session['akzioa'] = request.form.get('akzioa')
         
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

      taldea = session.get('editatzen_ari_den_taldea')
      if request.args.get('akzioa') is not None:
          akzioa = request.args.get('akzioa')
      else:
         akzioa = session.get('akzioa')

      if akzioa == 'hauta_pokemon':
         datuak = service.bistaratu_pokemon(id)
      else:
         datuak = service.bistaratu_pokemon_taldea(id)

      session['pokemon_datuak'] = id

      return render_template('pokemon.html', pokemon=datuak, taldea=taldea, akzioa=akzioa)
   return pokedex_bp