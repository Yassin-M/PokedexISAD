from flask import Blueprint, render_template, request, session
from app.controller.model.eredu_kontroladorea import EreduKontroladorea

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
      datuak = service.bistaratu_pokemon(id)

      return render_template('pokemon.html', pokemon=datuak)
   return pokedex_bp

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
        erabiltzaileIzena = session.get('username')
        pokemonOnenak=service.getOnenak({
            "taldeIzena": taldeIzena,
            "erabiltzaileIzena": erabiltzaileIzena
        })
        return render_template('onenak.html', taldea=pokemonOnenak)

    @chatbot_bp.route('/taldezerrenda')
    def taldeZerrenda():
        erabiltzaileIzena = session.get('username')
        taldeZerrenda = service.getTaldeZerrenda(erabiltzaileIzena)
        return render_template('taldeZerrenda.html', taldeak=taldeZerrenda)

    @chatbot_bp.route('/taldezerrenda_test')
    def taldeZerrenda_test():
        # 使用模拟数据测试HTML模板
        mock_taldeak = [
            {"taldeIzena": "LEHEN TALDEA"},
            {"taldeIzena": "BIGARREN TALDEA"},
            {"taldeIzena": "HIRUGARREN TALDEA"},
            {"taldeIzena": "LAUGARREN TALDEA"},
            {"taldeIzena": "BOSTGARREN TALDEA"},
            {"taldeIzena": "SEIGARREN TALDEA"},
            {"taldeIzena": "ZAZPIGARREN TALDEA"},
            {"taldeIzena": "ZORTZIGARREN TALDEA"},
            {"taldeIzena": "BEDERATZIGARREN TALDEA"},
            {"taldeIzena": "HAMARGARREN TALDEA"}
        ]

        return render_template('taldeZerrenda.html', taldeak=mock_taldeak)
    return chatbot_bp

