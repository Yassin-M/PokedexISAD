from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app.controller.model.eredu_kontroladorea import EreduKontroladorea
import json
import datetime

class BistaKontroladorea:
    def __init__(self, db):
        self.eredu_kontroladorea = EreduKontroladorea(db)
    
# =====================================================
# BLUEPRINTS (Nivel global de archivo)
# =====================================================    
    def saioHasi(self, erabiltzailea, pasahitza):
      """Saioa hasteko orria"""
      if request.method == 'POST':
        
         if not erabiltzailea or not pasahitza:
            flash('Mesedez, bete eremu guztiak', 'error')
            return redirect(url_for('login'))
         
         erantzuna_json = self.eredu_kontroladorea.saioHasi(erabiltzailea, pasahitza)
         erantzuna = json.loads(erantzuna_json or '{}')
         ondo = erantzuna.get('ondo')
         erabiltzaile_izena = erantzuna.get('erabiltzaile_izena')
         rola = erantzuna.get('rola')
         mezua = erantzuna.get('mezua')
         
         if ondo:
            session['user'] = erabiltzaile_izena
            session['role'] = rola or 'usuario'
            if (rola or '').lower() == 'admin':
               return redirect(url_for('menu_admin'))
            return redirect(url_for('menu'))
         else:
            flash(mezua, 'error')
            return redirect(url_for('login'))
      
      return render_template('login.html')
   
    def erregistratu(self):
        """Erregistro orria"""
        if request.method == 'POST':
            erabiltzailea = request.form.get('erabiltzailea')
            email = request.form.get('email')
            jaiotze_data = request.form.get('jaiotze_data')
            pasahitza = request.form.get('pasahitza')
            pasahitza2 = request.form.get('pasahitza_berretsi')
            error = None
            
            if not all([erabiltzailea, email, jaiotze_data, pasahitza, pasahitza2]):
                error = 'Mesedez, bete eremu guztiak'
            
            if error:
                flash(error, 'error')
                return redirect(url_for('register'))
            
            ondo, mensaje = self.eredu_kontroladorea.erregistratu(
                erabiltzailea, email, jaiotze_data, pasahitza, pasahitza2
            )
            
            if ondo:
                flash(mensaje + ' Saioa hasi dezakezu orain.', 'success')
                return redirect(url_for('login'))
            else:
                flash(mensaje, 'error')
                return redirect(url_for('register'))
        
        return render_template('register.html')
    
    def datuakAldatu(self, user_id=None):
        """Profila editatzeko orria"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        if user_id:
            if session.get('role', '').lower() != 'admin':
                flash('Ez duzu baimenik orri hau ikusteko', 'error')
                return redirect(url_for('menu'))
            erabiltzaile_izena = user_id
            home_endpoint = 'kudeatu'
        else:
            erabiltzaile_izena = session['user']
            home_endpoint = 'menu_admin' if (session['role'].lower() == 'admin') else 'menu'
      
        query = "SELECT izena, pasahitza, rola, email, jaiotze_data FROM Erabiltzailea WHERE izena = ?"
        emaitza_lista = self.eredu_kontroladorea.db.select(query, (erabiltzaile_izena,))
        emaitza = emaitza_lista[0] if emaitza_lista else None
      
        if request.method == 'POST':
            izena = request.form['izena'].strip() if request.form['izena'].strip() else None
            email = request.form['email'].strip() if request.form['email'].strip() else None
            jaiotze_data = request.form['jaiotza'].strip() if request.form['jaiotza'].strip() else None
            pasahitza = request.form['pasahitza'].strip() if request.form['pasahitza'].strip() else None
            pasahitza2 = request.form['pasahitza2'].strip() if request.form['pasahitza2'].strip() else None
            
            if pasahitza or pasahitza2:
                if pasahitza != pasahitza2:
                    flash('Pasahitzak ez datoz bat', 'error')
                    return redirect(url_for('editatu', user_id=user_id) if user_id else url_for('editatu'))
                
                baliozko, mezua = self.eredu_kontroladorea.balioztatu_pasahitza(pasahitza, pasahitza2)
                if not baliozko:
                    flash(mezua, 'error')
                    return redirect(url_for('editatu', user_id=user_id) if user_id else url_for('editatu'))
          
            eguneratu_json = self.eredu_kontroladorea.eguneratu_erabiltzailea(
                erabiltzaile_izena, izena, email, jaiotze_data, pasahitza
            )
            eguneratu = json.loads(eguneratu_json or '{}')
            ondo = eguneratu.get('ondo')
            mezua = eguneratu.get('mezua')
          
            if ondo:
                if izena and not user_id:
                    session['user'] = izena
                flash(mezua, 'success')
                if user_id:
                    return redirect(url_for('kudeatu'))
                return redirect(url_for('editatu'))
            else:
                flash(mezua, 'error')
                return redirect(url_for('editatu', user_id=user_id) if user_id else url_for('editatu'))
      
        return render_template('editatu.html', home_endpoint=home_endpoint, erabiltzailea=emaitza)
    
    def erabiltzaileakKargatu(self):
        """Erabiltzaileak kudeatzeko orria (administratzaileak bakarrik)"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        if session.get('role', '').lower() != 'admin':
            flash('Ez duzu baimenik orri hau ikusteko', 'error')
            return redirect(url_for('menu'))
        
        erabiltzaileak_json = self.eredu_kontroladorea.erabiltzaileakKargatu()
        erabiltzaileak = json.loads(erabiltzaileak_json)
        
        current_user = session.get('user')
        erabiltzaileak = [user for user in erabiltzaileak if user.get('izena') != current_user]
        home_endpoint = 'menu_admin'
        
        return render_template('kudeatu.html', users=erabiltzaileak, home_endpoint=home_endpoint)
    
    def ezabatu(self, user_id):
        """Erabiltzaile bat ezabatu (administratzaileak bakarrik)"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        if session.get('role', '').lower() != 'admin':
            flash('Ez duzu baimenik', 'error')
            return redirect(url_for('menu'))
        
        query = "SELECT rola FROM Erabiltzailea WHERE izena = ?"
        emaitza = self.eredu_kontroladorea.db.select(query, (user_id,))
        
        if not emaitza:
            flash('Erabiltzailea ez da aurkitu', 'error')
            return redirect(url_for('kudeatu'))
        
        if session['user'] == user_id:
            flash('Ezin duzu zure burua ezabatu', 'error')
            return redirect(url_for('kudeatu'))
        
        emaitza_json = self.eredu_kontroladorea.ezabatu(user_id)
        emaitza = json.loads(emaitza_json or '{}')
        ondo = emaitza.get('ondo')
        mezua = emaitza.get('mezua')
        if ondo:
            flash(mezua, 'success')
        else:
            flash(mezua, 'error')
        return redirect(url_for('kudeatu'))
    
    def baimendu(self, user_id):
        """Erabiltzaile bat admin bihurtu (administratzaileak bakarrik)"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        if session.get('role', '').lower() != 'admin':
            flash('Ez duzu baimenik', 'error')
            return redirect(url_for('menu'))
        
        emaitza_json = self.eredu_kontroladorea.baimendu(user_id, True)
        emaitza = json.loads(emaitza_json or '{}')
        ondo = emaitza.get('ondo')
        mezua = emaitza.get('mezua')
        if ondo:
            flash(mezua, 'success')
        else:
            flash(mezua, 'error')
        return redirect(url_for('kudeatu'))
    
    def lagunakKargatu(self):
        """Jarraitzen dituen pertsonak ikusi"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        current_user = session.get('user')
        jarraitutakoak_json = self.eredu_kontroladorea.lagunakKargatu(current_user)
        jarraitutakoak = json.loads(jarraitutakoak_json)
        
        if session.get('role', '').lower() == 'admin':
            menu_endpoint = 'menu_admin'
        else:
            menu_endpoint = 'menu'
        
        return render_template('lagunak.html', lagunak=jarraitutakoak, menu_endpoint=menu_endpoint)
    
    def utzi_jarraitzen(self, jarraitua):
        """Erabiltzaile bat jarraitzen uztea"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        current_user = session.get('user')
        emaitza_json = self.eredu_kontroladorea.utzi_jarraitzen(current_user, jarraitua)
        emaitza = json.loads(emaitza_json or '{}')
        ondo = emaitza.get('ondo')
        mezua = emaitza.get('mezua')
        if ondo:
            flash(mezua, 'success')
        else:
            flash(mezua, 'error')
        return redirect(url_for('lagunak'))
    
    def gehituErabiltzailea(self, jarraitua=None):
        """Erabiltzaileak bilatu eta jarraitu"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        current_user = session.get('user')
        if jarraitua:
            emaitza_json = self.eredu_kontroladorea.gehituErabiltzailea(current_user, jarraitua)
            emaitza = json.loads(emaitza_json or '{}')
            ondo = emaitza.get('ondo')
            mezua = emaitza.get('mezua')
            if ondo:
                flash(mezua, 'success')
            else:
                flash(mezua, 'error')
            bilaketa = request.args.get('bilaketa', '')
            return redirect(url_for('gehituErabiltzailea', bilaketa=bilaketa))
      
        bilaketa = request.args.get('bilaketa', '')
        if session.get('role', '').lower() == 'admin':
            menu_endpoint = 'menu_admin'
        else:
            menu_endpoint = 'menu'
      
        erabiltzaileak = []
        if bilaketa:
            erabiltzaileak_json = self.eredu_kontroladorea.bilatu_erabiltzaileak(bilaketa, current_user)
            erabiltzaileak = json.loads(erabiltzaileak_json)
      
        return render_template('bilatzailea.html', erabiltzaileak=erabiltzaileak,
                               bilaketa=bilaketa, menu_endpoint=menu_endpoint)
    
    def eguneratu_notifikazioak(self, jarraitua):
        if 'user' not in session:
            return redirect(url_for('login'))
        
        current_user = session.get('user')
        isilarazi = request.args.get('isilarazi', 'False').lower() == 'true'
        emaitza_json = self.eredu_kontroladorea.eguneratu_notifikazioak(current_user, jarraitua, isilarazi)
        emaitza = json.loads(emaitza_json or '{}')
        mezua = emaitza.get('mezua')
        if mezua:
            flash(mezua, 'success' if emaitza.get('ondo') else 'error')
        return redirect(url_for('lagunak'))


def taldeak_blueprint(db):
    taldeak_bp = Blueprint('taldeak', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @taldeak_bp.route('/taldeak', methods=['GET', 'POST'])
    def taldeak_kargatu():
        # Aurretik talde bat bazegoen editatzen, atera. 
        session.pop('editatzen_ari_den_taldea', None)
        
        # Erabiltzailea eta rola hartu saioatik
        erabiltzailea = session.get('user')
        user_role = session.get('role', 'usuario')

        # Taldeak kargatu
        talde_zerrenda = service.taldeak_kargatu(erabiltzailea)

        # Menu egokia aukeratu rolaren arabera
        menu_endpoint = 'menu_admin' if user_role.lower() == 'admin' else 'menu'

        # Taldeen zerrenda erakutsi
        return render_template('taldeak.html', taldeak=talde_zerrenda, menu_endpoint=menu_endpoint)
    
    @taldeak_bp.route('/taldea', methods=['GET', 'POST'])
    def taldea_dago():
        # Talde izena hartu form-etik edo saioatik
        talde_izena = request.form.get('talde_izena') or session.get('editatzen_ari_den_taldea')

        # Taldea badago, berreraman taldea ikustera
        if talde_izena:
            return redirect(url_for('taldeak.taldea', izena=talde_izena))
        # Bestela taldeen zerrendara eramango gaitu
        flash("Ez da talderik zehaztu", "error")
        return redirect(url_for('taldeak.taldeak_kargatu'))

    @taldeak_bp.route('/taldea/<string:izena>', methods=['GET', 'POST'])
    def taldea(izena=None):
        # Talde izena hartu form-etik, parametroetatik edo saioatik
        talde_izena = izena or request.form.get('talde_izena') or session.get('editatzen_ari_den_taldea')

        # Taldea ez badago, taldeen zerrendara eramango gaitu
        if not talde_izena:
            flash("Ez da talderik zehaztu", "error")
            return redirect(url_for('taldeak.taldeak_kargatu'))
        
        # Taldea saioan sartu
        session['editatzen_ari_den_taldea'] = talde_izena

        # Erabiltzailea eta rola hartu saioatik
        erabiltzailea = session.get('user')
        user_role = session.get('role', 'usuario')

        # Talde datuak kargatu
        talde_datuak = service.get_taldea(talde_izena, erabiltzailea)

        # Menu egokia aukeratu rolaren arabera
        menu_endpoint = 'menu_admin' if user_role.lower() == 'admin' else 'menu'

        # Talde orria erakutsi
        return render_template('taldea.html', pokemons=talde_datuak, menu_endpoint=menu_endpoint, taldea_izena=talde_izena)

    @taldeak_bp.route('/taldea_berria', methods=['POST'])
    def sortu_taldea():
        try:
            # Erabiltzailea hartu saiotik
            erabiltzailea = session.get('user')

            # Talde huts bat sortu eta saioan gorde editatzen ari den taldea bezala
            taldea_id = service.sortu_taldea_hutsa(erabiltzailea)  
            session['editatzen_ari_den_taldea'] = taldea_id

            # Notifikazioa sortu
            deskripzioa = f"Talde berria sortu du: {taldea_id}."
            service.notifikazioBerria(erabiltzailea, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), deskripzioa)

            # Taldea erakutsi
            return redirect(url_for('taldeak.taldea', izena=taldea_id))
        except ValueError as e:
            # Errorea eman bada, talde zerrendara bueltatu eta errorea erakutsi
            flash(str(e), "error")
            return redirect(url_for('taldeak.taldeak_kargatu'))
    
    @taldeak_bp.route('/pokemon_taldea', methods=['POST'])
    def sartu_taldera():
        # Talde izena eta pokemon ID hartu saiotik
        talde_izena = session.get('editatzen_ari_den_taldea')
        pokemon_id = session.get('pokemon_datuak')
        try:
            # Erabiltzailea hartu saiotik
            erabiltzailea = session.get('user')

            # Pokemon-a taldean sartu
            pokeIzena = service.sartu_taldera(talde_izena, erabiltzailea, pokemon_id)

            # Notifikazioa sortu
            service.notifikazioBerria(erabiltzailea, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{pokeIzena} bat gehitu du {talde_izena} taldean.")

            # Taldea erakutsi
            return redirect(url_for('taldeak.taldea_dago'))
        except ValueError as e:
            # Errorea eman bada, talde orrira bueltatu eta errorea erakutsi
            flash(str(e), "error")
            return redirect(url_for('taldeak.taldea_dago'))
    
    @taldeak_bp.route('/pokemon_taldea/ezabatu', methods=['GET', 'POST'])
    def ezabatu_taldetik():
        # Erabiltzailea, talde izena eta pokemon ID hartu saiotik
        erabiltzailea = session.get('user')
        talde_izena = session.get('editatzen_ari_den_taldea')
        pokemon_id = session.get('pokemon_datuak')

        # Pokemon-a taldeatik ezabatu
        pokeIzena = service.ezabatu_taldetik(talde_izena, erabiltzailea, pokemon_id)

        # Notifikazioa sortu
        service.notifikazioBerria(erabiltzailea, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{pokeIzena} bat ezabatu du {talde_izena} taldean.")

        # Akzioaren arabera birbideratu
        akzioa = request.args.get('akzioa')

        # Pokemon berri bat hautatu behar bada, pokedex-era bideratu
        if akzioa == 'hauta_pokemon':
            session['akzioa'] = 'aldatu'
            return redirect(url_for('pokedex.pokedex'))
        # Bestela, taldea berriro erakutsi
        return redirect(url_for('taldeak.taldea_dago'))

    @taldeak_bp.route('/taldea/ezabatu_guztia', methods=['GET', 'POST'])
    def taldea_ezabatu():
        # Erabiltzailea eta talde izena hartu saiotik
        erabiltzailea = session.get('user')
        talde_izena = session.get('editatzen_ari_den_taldea')

        # Taldea ezabatu
        service.ezabatu_taldea(talde_izena, erabiltzailea)

        # Notifikazioa sortu
        service.notifikazioBerria(erabiltzailea, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{talde_izena} taldea ezabatu du.")

        # Talde zerrendara bueltatu
        return redirect(url_for('taldeak.taldeak_kargatu'))
    
    return taldeak_bp

def pokedex_blueprint(db):
    pokedex_bp = Blueprint('pokedex', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)
    @pokedex_bp.context_processor
    def inject_menu_endpoint():
        user_role = session.get('role', 'usuario')
        menu_endpoint = 'menu_admin' if user_role.lower() == 'admin' else 'menu'
        return dict(menu_endpoint=menu_endpoint)

    @pokedex_bp.route('/pokedex', methods=['GET', 'POST'])
    @pokedex_bp.route('/pokedex/bilatu', methods=['GET', 'POST'])
    def pokedex():
        iragazkiak = {'izena': None, 'generazioak': [], 'motak': []}
        mode = request.args.get('mode', 'info')
        if request.method == 'POST':
            mode = request.form.get('mode', mode)
            izena = request.form.get('izena')
            if izena: iragazkiak['izena'] = izena
            generazioak = request.form.getlist('generazioak')
            if generazioak: iragazkiak['generazioak'] = generazioak
            motak = request.form.getlist('motak')
            if motak: iragazkiak['motak'] = motak

        if request.form.get('akzioa') is not None:
            session['akzioa'] = request.form.get('akzioa')
        elif session.get('akzioa') == 'aldatu':
            session['akzioa'] = 'hauta_pokemon'
        else:
            session.pop('akzioa', None)

        pokemon_zerrenda = service.pokedex_kargatu(iragazkiak)
        return render_template('pokedex.html', pokemons=pokemon_zerrenda, mode=mode)

    @pokedex_bp.route('/pokedex/pokemon/<int:id>', methods=['GET'])
    def pokemon(id):
        # Editatzen ari den taldea saiotik hartu
        taldea = session.get('editatzen_ari_den_taldea')

        # Akzioa hartu parametrotik edo saioatik
        akzioa = request.args.get('akzioa') or session.get('akzioa')
        # Ez badago akziorik edo hautatu nahi bada, Pokemon-a erakutsi
        if akzioa == 'hauta_pokemon' or akzioa is None:
            datuak = service.bistaratu_pokemon(id)
        # Bestela, pokemon-a taldearen barruan editatzen bada, taldeko pokemon-a erakutsi (Dituen estatistikak (ATK, SP.ATK, DEF, SP.DEF, SPD, HP), mugimenduak eta abileziak)
        else:
            datuak = service.bistaratu_pokemon_taldea(id)

        # Pokemon ID saioan gorde taldera gehitzeko edo ezabatzeko    
        session['pokemon_datuak'] = id
        return render_template('pokemon.html', pokemon=datuak, taldea=taldea, akzioa=akzioa)
    return pokedex_bp

def itemdex_blueprint(db):
    bp = Blueprint("itemdex", __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @bp.context_processor
    def inject_menu_endpoint():
        user_role = session.get('role', 'usuario')
        menu_endpoint = 'menu_admin' if user_role.lower() == 'admin' else 'menu'
        return dict(menu_endpoint=menu_endpoint)

    @bp.route("/itemdex", methods=["GET", "POST"])
    def itemdex():
        if 'user' not in session:
            return redirect(url_for('login'))
        iragazkiak = {"izena": "", "motak": [], "alfabetikokiAlderantziz": False}
        if request.method == "POST":
            iragazkiak["izena"] = request.form.get("izena", "")
            iragazkiak["motak"] = request.form.getlist("motak")
            iragazkiak["alfabetikokiAlderantziz"] = (request.form.get("orden") == "desc")
        items = list(service.itemdex_kargatu(iragazkiak))
        motak = service.lortu_motak()
        return render_template("itemdex.html", items=items, motak=motak, service=service)

    @bp.route("/itemdex/item/<int:id>")
    def item(id):
        if 'user' not in session:
            return redirect(url_for('login'))
        item = service.bistaratu_item(id)
        return render_template("item.html", item=item)
    return bp

def bista_blueprint(db):
    bista_bp = Blueprint('bista_orokorra', __name__)

    @bista_bp.route('/changelog')
    def changelog():
        # Erabiltzailearen informazio hartu (rola, izena eta zeozer bilatu baldin badu ala ez)
        erabiltzailea = session.get('user')
        erabiltzaile_rola = session.get('role', 'usuario')
        bilatutakoIzena = request.args.get('bilatutako_erabiltzaile_izena')
        # Eredu kontroladorearen metodoa erabili notifikazioak lortzeko
        service = EreduKontroladorea(db)
        notifikazio_zerrenda = service.notifikazioenInformazioaLortu(erabiltzailea, bilatutakoIzena)
        # HTML-ari pasatu erabiltzailearen rolaren informazioa menu egokia erakusteko atzera egiterakoan
        menu_endpoint = 'menu_admin' if erabiltzaile_rola.lower() == 'admin' else 'menu'
        # Lortu den informazio guztia changelog.html-ra pasatu eta orria erakutsi
        return render_template('changelog.html', notifikazioak=notifikazio_zerrenda, menu_endpoint=menu_endpoint)
    
    return bista_bp

def chatbot_blueprint(db):
    chatbot_bp = Blueprint('chatbot', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @chatbot_bp.context_processor
    def inject_menu_endpoint():
        user_role = session.get('role', 'usuario')
        menu_endpoint = 'menu_admin' if user_role.lower() == 'admin' else 'menu'
        return dict(menu_endpoint=menu_endpoint)

    @chatbot_bp.route('/chatbot')
    def chatbot_menu():
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('chatbot.html')

    @chatbot_bp.route('/chatbot/mugimenduak/<int:id>')
    def getMugimenduIkasgarriak(id):
        if 'user' not in session:
            return redirect(url_for('login'))

        pokemonMugimenduak = service.getMugimenduIkasgarriak(id)
        return render_template('mugimenduak.html', pokemon=pokemonMugimenduak)

    @chatbot_bp.route('/chatbot/eboluzioa/<int:id>')
    def getEboluzioa(id):
        if 'user' not in session:
            return redirect(url_for('login'))

        pokemonEboluzioa = service.getEboluzioa(id)
        return render_template('eboluzioa.html', pokemon=pokemonEboluzioa)

    @chatbot_bp.route('/chatbot/indarrak/<int:id>')
    def getIndarrak(id):
        if 'user' not in session:
            return redirect(url_for('login'))

        pokemonIndarrak = service.getIndarrak(id)
        return render_template("indarrak.html", pokemon=pokemonIndarrak)

    @chatbot_bp.route('/chatbot/taldeZerrenda')
    def taldeZerrenda():
        if 'user' not in session:
            return redirect(url_for('login'))
        user = session.get('user')
        talde_zerrenda = service.taldeak_kargatu(user)
        return render_template('taldeZerrenda.html', taldeak=talde_zerrenda)

    @chatbot_bp.route('/chatbot/onenak/<taldeIzena>')
    def getOnenak(taldeIzena):
        if 'user' not in session:
            return redirect(url_for('login'))
        user = session.get('user')
        pokemonOnenak = service.getOnenak({
            "taldeIzena": taldeIzena,
            "erabiltzaileIzena": user
        })
        return render_template('onenak.html', pokemon=pokemonOnenak)

    return chatbot_bp
