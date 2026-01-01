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