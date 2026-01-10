from flask import flash, Blueprint, render_template, request, redirect, session, url_for
from app.controller.model.eredu_kontroladorea import EreduKontroladorea
import datetime

# =====================================================
# TALDEAK
# =====================================================
def taldeak_blueprint(db):
   taldeak_bp = Blueprint('taldeak', __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   talde_zerrenda = service.taldeak_kargatu('juan')
   print("Loaded taldeak:", talde_zerrenda)  # Debugging output

   @taldeak_bp.route('/taldeak', methods=['GET', 'POST'])
   def taldeak_kargatu():
      session.pop('editatzen_ari_den_taldea', None)
      talde_zerrenda = service.taldeak_kargatu('juan')
      return render_template('taldeak.html', taldeak=talde_zerrenda)
   
   @taldeak_bp.route('/taldea', methods=['GET', 'POST'])
   def taldea_dago():
      talde_izena = request.form.get('talde_izena') or session.get('editatzen_ari_den_taldea')

      if talde_izena:
         return redirect(url_for('taldeak.taldea', izena=talde_izena))
       
      flash("Ez da talderik zehaztu", "error")
      return redirect(url_for('taldeak.taldeak_kargatu'))

   @taldeak_bp.route('/taldea/<string:izena>', methods=['GET', 'POST'])
   def taldea(izena=None):
      talde_izena = izena or request.form.get('talde_izena') or session.get('editatzen_ari_den_taldea')

      if not talde_izena:
        flash("Ez da talderik zehaztu", "error")
        return redirect(url_for('taldeak.taldeak_kargatu'))
      
      session['editatzen_ari_den_taldea'] = talde_izena
      talde_datuak = service.get_taldea(talde_izena, 'juan')
      return render_template('taldea.html', pokemons=talde_datuak)


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
   
   #@taldeak_bp.route('/editatu_taldea', methods=['GET', 'POST'])
   #def kargatu_taldea():
      
   #   if request.form.get('talde_izena'):
   #      talde_izena = request.form.get('talde_izena')
   #      session['editatzen_ari_den_taldea'] = talde_izena
   #   else:
   #      talde_izena = session.get('editatzen_ari_den_taldea')
   #   talde_datuak = service.get_taldea(talde_izena, 'juan')
   #   return render_template('taldea.html', pokemons=talde_datuak, izena=talde_izena)
   
   @taldeak_bp.route('/pokemon_taldea', methods=['POST'])
   def sartu_taldera():
      talde_izena = session.get('editatzen_ari_den_taldea')
      pokemon_id = session.get('pokemon_datuak')
      try:
         pokeIzena = service.sartu_taldera(talde_izena, 'juan', pokemon_id)
         service.notifikazioBerria('juan', f"{pokeIzena} bat gehitu du {talde_izena} taldean.", datetime.datetime.now())
         return redirect(url_for('taldeak.taldea_dago')) #Cambios
      except ValueError as e:
         flash(str(e), "error")
         return redirect(url_for('taldeak.taldea_dago')) # Cambios
   
   @taldeak_bp.route('/pokemon_taldea/ezabatu', methods=['GET', 'POST'])
   def ezabatu_taldetik():
      talde_izena = session.get('editatzen_ari_den_taldea')
      pokemon_id = session.get('pokemon_datuak')
      pokeIzena = service.ezabatu_taldetik(talde_izena, 'juan', pokemon_id)
      service.notifikazioBerria('juan', f"{pokeIzena} bat ezabatu du {talde_izena} taldean.", datetime.datetime.now())

      akzioa = request.args.get('akzioa')
      if akzioa == 'hauta_pokemon':
         session['akzioa'] = 'aldatu'
         print(session['akzioa'])
         return redirect(url_for('pokedex.pokedex'))
      else:
         return redirect(url_for('taldeak.taldea_dago'))  #Cambios

   @taldeak_bp.route('/taldea/ezabatu', methods=['GET', 'POST'])
   def taldea_ezabatu():
      talde_izena = session.get('editatzen_ari_den_taldea')
      service.ezabatu_taldea(talde_izena, 'juan')
      service.notifikazioBerria('juan', f"{talde_izena} taldea ezabatu du.", datetime.datetime.now())
      return redirect(url_for('taldeak.taldeak_kargatu'))
   
   return taldeak_bp

# =====================================================
# POKEDEX
# =====================================================
def pokedex_blueprint(db):
   pokedex_bp = Blueprint('pokedex', __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   @pokedex_bp.route('/pokedex', methods=['GET', 'POST'])
   @pokedex_bp.route('/pokedex/bilatu', methods=['GET', 'POST'])
   def pokedex():
      iragazkiak = {'izena': None, 'generazioak': [], 'motak': []}
      mode = request.args.get('mode', 'info')

      if request.method == 'POST':
         mode = request.form.get('mode', mode)
      
      if request.form.get('akzioa') is not None:
         session['akzioa'] = request.form.get('akzioa')
      elif session.get('akzioa') == 'aldatu':
         session['akzioa'] = 'hauta_pokemon'
      else:
         session.pop('akzioa', None)

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
      return render_template('pokedex.html', pokemons=pokemon_zerrenda, mode=mode)

   @pokedex_bp.route('/pokedex/pokemon/<int:id>', methods=['GET'])
   def pokemon(id):

      taldea = session.get('editatzen_ari_den_taldea')
      if request.args.get('akzioa') is not None:
          akzioa = request.args.get('akzioa')
      else:
         akzioa = session.get('akzioa')

      if akzioa == 'hauta_pokemon' or akzioa == None:
         datuak = service.bistaratu_pokemon(id)
      else:
         datuak = service.bistaratu_pokemon_taldea(id)

      session['pokemon_datuak'] = id

      return render_template('pokemon.html', pokemon=datuak, taldea=taldea, akzioa=akzioa)
   return pokedex_bp

# =====================================================
# ITEMDEX
# =====================================================
def itemdex_blueprint(db):

   bp = Blueprint("itemdex", __name__, template_folder="../../templates")
   service = EreduKontroladorea(db)

   @bp.route("/itemdex", methods=["GET", "POST"])
   def itemdex():
        iragazkiak = {
            "izena": "",
            "motak": [],
            "alfabetikokiAlderantziz": False
        }

        if request.method == "POST":
            iragazkiak["izena"] = request.form.get("izena", "")
            iragazkiak["motak"] = request.form.getlist("motak")
            iragazkiak["alfabetikokiAlderantziz"] = (
                request.form.get("orden") == "desc"
            )

        items = list(service.itemdex_kargatu(iragazkiak))
        motak = service.lortu_motak()  # obtenemos los tipos desde la DB
        return render_template("itemdex.html", items=items, motak=motak, service=service)

   @bp.route("/itemdex/item/<int:id>")
   def item(id):
        item = service.bistaratu_item(id)
        return render_template("item.html", item=item)

   return bp

# =====================================================
# CHANGELOG
# =====================================================
from flask import Blueprint, render_template, request, session
from app.controller.model import eredu_kontroladorea
bista_bp = Blueprint('bista_orokorra', __name__)

@bista_bp.route('/changelog')
def changelog():
    ErabiltzaileIzena = session.get('username')

    bilatutakoIzena = request.args.get('bilatutako_erabiltzaile_izena')

    lista_notificaciones = eredu_kontroladorea.notifikazioenInformazioaLortu(ErabiltzaileIzena, bilatutakoIzena)

    return render_template('changelog.html', notificaciones=lista_notificaciones)

# =====================================================
# CHATBOT
# =====================================================
def chatbot_blueprint(db):
    chatbot_bp = Blueprint('chatbot', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)
    #service.create_simple_test_team()

    @chatbot_bp.route('/chatbot')
    def chatbot_menu():
        return render_template('chatbot.html')

    @chatbot_bp.route('/chatbot/mugimenduak/<int:id>')
    def getMugimenduIkasgarriak(id):
        pokemonMugimenduak = service.getMugimenduIkasgarriak(id)
        return render_template('mugimenduak.html', pokemon=pokemonMugimenduak)

    @chatbot_bp.route('/chatbot/eboluzioa/<int:id>')
    def getEboluzioa(id):
        pokemonEboluzioa = service.getEboluzioa(id)
        return render_template('eboluzioa.html', pokemon=pokemonEboluzioa)

    @chatbot_bp.route('/chatbot/indarrak/<int:id>')
    def getIndarrak(id):
        pokemonIndarrak = service.getIndarrak(id)
        return render_template("indarrak.html", pokemon=pokemonIndarrak)

    @chatbot_bp.route('/onenak/<taldeIzena>')
    def getOnenak(taldeIzena):
        #erabiltzaileIzena = session.get('username')
        pokemonOnenak=service.getOnenak({
            "taldeIzena": taldeIzena,
            "erabiltzaileIzena": "test_user"
        })
        return render_template('onenak.html', pokemon=pokemonOnenak)

    @chatbot_bp.route('/chatbot/taldeZerrenda')
    def taldeZerrenda():
        #erabiltzaileIzena = session.get('username')
        taldeZerrenda = service.taldeak_kargatu("test_user")
        return render_template('taldeZerrenda.html', taldeak=taldeZerrenda)

    return chatbot_bp
