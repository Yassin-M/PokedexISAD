import json
from flask import Blueprint, render_template, request
from app.controller.model.eredu_kontroladorea import EreduKontroladorea

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

def chatbot_blueprint(db):
    chatbot_bp = Blueprint('chatbot', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @chatbot_bp.route('/chatbot')
    def chatbot_menu():
        return render_template('chatbot.html')

    @chatbot_bp.route('/chatbot/mugimenduak/<int:id>')
    def mugimenduak(id):
        mugimenduak = service.getMugimenduIkasgarriak(id)
        return render_template('mugimenduak.html', pokemon=mugimenduak)

    @chatbot_bp.route('/chatbot/onenak/<int:id>')
    def onenak(id):
        pokemon = service.bistaratu_pokemon(id)
        return render_template('onenak.html', pokemon=pokemon)

    @chatbot_bp.route('/chatbot/eboluzioa/<int:id>')
    def eboluzioa(id):
        pokemon = service.getEboluzioa(id)
        return render_template('eboluzioa.html', pokemon=pokemon)

    @chatbot_bp.route('/chatbot/indarrak/<int:id>')
    def indarrak(id):
        indarrak_json = service.getIndarrak(id)
        pokemon = json.loads(indarrak_json)
        return render_template("indarrak.html", pokemon=pokemon)

    return chatbot_bp

