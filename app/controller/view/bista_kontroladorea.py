from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from app.controller.model.eredu_kontroladorea import EreduKontroladorea
import json
import datetime

class BistaKontroladorea:
    def __init__(self, db):
        self.eredu_kontroladorea = EreduKontroladorea(db)
    
    def saioHasi(self, erabiltzailea, pasahitza):
      """Saioa hasteko orria"""
      if request.method == 'POST':
        
         if not erabiltzailea or not pasahitza:
            error = 'Mesedez, bete eremu guztiak'
            return render_template('login.html', error=error)
         
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
               return redirect('menu_admin.html')
            return redirect('menu.html')
         else:
            error = mezua
            return render_template('login.html', error=error)
      
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
                return render_template('register.html', error=error)
            
            ondo, mensaje = self.eredu_kontroladorea.erregistratu(
                erabiltzailea, email, jaiotze_data, pasahitza, pasahitza2
            )
            
            if ondo:
                success = mensaje + ' Saioa hasi dezakezu orain.'
                return render_template('register.html', success=success)
            else:
                error = mensaje
                return render_template('register.html', error=error)
        
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
                    return render_template('editatu.html', home_endpoint=home_endpoint, 
                                        erabiltzailea=emaitza, error='Pasahitzak ez datoz bat')
                
                baliozko, mezua = self.eredu_kontroladorea.balioztatu_pasahitza(pasahitza, pasahitza2)
                if not baliozko:
                    return render_template('editatu.html', home_endpoint=home_endpoint,
                                        erabiltzailea=emaitza, error=mezua)
          
            ondo, mezua = self.eredu_kontroladorea.eguneratu_erabiltzailea(
                erabiltzaile_izena, izena, email, jaiotze_data, pasahitza
            )
          
            if ondo:
                if izena and not user_id:
                    session['user'] = izena
                if user_id:
                    return redirect(url_for('kudeatu'))
                berria = izena if izena else erabiltzaile_izena
                emaitza_lista = self.eredu_kontroladorea.db.select(query, (berria,))
                emaitza = emaitza_lista[0] if emaitza_lista else None
                return render_template('editatu.html', home_endpoint=home_endpoint,
                                     erabiltzailea=emaitza, success=mezua)
            else:
                return render_template('editatu.html', home_endpoint=home_endpoint,
                                     erabiltzailea=emaitza, error=mezua)
      
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
        
        ondo, mezua = self.eredu_kontroladorea.ezabatu(user_id)
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
        
        ondo, mezua = self.eredu_kontroladorea.baimendu(user_id, True)
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
        ondo, mezua = self.eredu_kontroladorea.utzi_jarraitzen(current_user, jarraitua)
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
            ondo, mezua = self.eredu_kontroladorea.gehituErabiltzailea(current_user, jarraitua)
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
        self.eredu_kontroladorea.eguneratu_notifikazioak(current_user, jarraitua, isilarazi)
        return redirect(url_for('lagunak'))


# =====================================================
# BLUEPRINTS (Nivel global de archivo)
# =====================================================

def taldeak_blueprint(db):
    taldeak_bp = Blueprint('taldeak', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

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

    @taldeak_bp.route('/taldea_berria', methods=['POST'])
    def sortu_taldea():
        try:
            taldea_id = service.sortu_taldea_hutsa('juan')  
            session['editatzen_ari_den_taldea'] = taldea_id
            deskripzioa = f"Talde berria sortu du: {taldea_id}."
            service.notifikazioBerria('juan', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), deskripzioa)
            return redirect(url_for('taldeak.taldea', izena=taldea_id))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('taldeak.taldeak_kargatu'))
    
    @taldeak_bp.route('/pokemon_taldea', methods=['POST'])
    def sartu_taldera():
        talde_izena = session.get('editatzen_ari_den_taldea')
        pokemon_id = session.get('pokemon_datuak')
        try:
            pokeIzena = service.sartu_taldera(talde_izena, 'juan', pokemon_id)
            service.notifikazioBerria('juan', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{pokeIzena} bat gehitu du {talde_izena} taldean.")
            return redirect(url_for('taldeak.taldea_dago'))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('taldeak.taldea_dago'))
    
    @taldeak_bp.route('/pokemon_taldea/ezabatu', methods=['GET', 'POST'])
    def ezabatu_taldetik():
        talde_izena = session.get('editatzen_ari_den_taldea')
        pokemon_id = session.get('pokemon_datuak')
        pokeIzena = service.ezabatu_taldetik(talde_izena, 'juan', pokemon_id)
        service.notifikazioBerria('juan', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{pokeIzena} bat ezabatu du {talde_izena} taldean.")
        akzioa = request.args.get('akzioa')
        if akzioa == 'hauta_pokemon':
            session['akzioa'] = 'aldatu'
            return redirect(url_for('pokedex.pokedex'))
        return redirect(url_for('taldeak.taldea_dago'))

    @taldeak_bp.route('/taldea/ezabatu_guztia', methods=['GET', 'POST'])
    def taldea_ezabatu():
        talde_izena = session.get('editatzen_ari_den_taldea')
        service.ezabatu_taldea(talde_izena, 'juan')
        service.notifikazioBerria('juan', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{talde_izena} taldea ezabatu du.")
        return redirect(url_for('taldeak.taldeak_kargatu'))
    
    return taldeak_bp

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
        taldea = session.get('editatzen_ari_den_taldea')
        akzioa = request.args.get('akzioa') or session.get('akzioa')
        if akzioa == 'hauta_pokemon' or akzioa is None:
            datuak = service.bistaratu_pokemon(id)
        else:
            datuak = service.bistaratu_pokemon_taldea(id)
        session['pokemon_datuak'] = id
        return render_template('pokemon.html', pokemon=datuak, taldea=taldea, akzioa=akzioa)
    return pokedex_bp

def itemdex_blueprint(db):
    bp = Blueprint("itemdex", __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @bp.route("/itemdex", methods=["GET", "POST"])
    def itemdex():
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
        item = service.bistaratu_item(id)
        return render_template("item.html", item=item)
    return bp

def bista_blueprint(db):
    bista_bp = Blueprint('bista_orokorra', __name__)

    @bista_bp.route('/changelog')
    def changelog():
        current_user = session.get('user')
        bilatutakoIzena = request.args.get('bilatutako_erabiltzaile_izena')
        service = EreduKontroladorea(db)
        lista_notificaciones = service.notifikazioenInformazioaLortu(current_user, bilatutakoIzena)
        return render_template('changelog.html', notificaciones=lista_notificaciones)
    
    return bista_bp

def chatbot_blueprint(db):
    chatbot_bp = Blueprint('chatbot', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

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
        pokemonOnenak = service.getOnenak({
            "taldeIzena": taldeIzena,
            "erabiltzaileIzena": "test_user"
        })
        return render_template('onenak.html', pokemon=pokemonOnenak)

    @chatbot_bp.route('/chatbot/taldeZerrenda')
    def taldeZerrenda():
        talde_zerrenda = service.taldeak_kargatu("test_user")
        return render_template('taldeZerrenda.html', taldeak=talde_zerrenda)

    return chatbot_bp
