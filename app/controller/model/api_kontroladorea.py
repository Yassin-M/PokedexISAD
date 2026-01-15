import pokebase as pb
import requests

class APIKontroladorea:

   def __init__(self):
    self.erromatarrak = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9}
    self.base_url = "https://pokeapi.co/api/v2/"
    self.traducciones_tipos = {
            "standard-balls": "Poké Balls estándar",
            "special-balls": "Poké Balls especiales",
            "apricorn-balls": "Poké Balls de Bayas",
            "healing": "Curación",
            "status-cures": "Cura estados",
            "pp-recovery": "Recupera PP",
            "revival": "Revivir",
            "vitamins": "Vitaminas",
            "stat-boosts": "Mejora estadísticas",
            "medicine": "Medicina",
            "picky-healing": "Curación exigente",
            "baking-only": "Solo para hornear",
            "type-protection": "Protección tipo",
            "in-a-pinch": "En apuros",
            "held-items": "Objetos equipables",
            "bad-held-items": "Objetos equipables malos",
            "choice": "Elección",
            "type-enhancement": "Mejora de tipo",
            "training": "Entrenamiento",
            "effort-training": "Entrenamiento esfuerzo",
            "effort-drop": "Aumento esfuerzo",
            "all-machines": "Todas las máquinas",
            "machines": "Máquinas",
            "machine": "Máquina",
            "species-specific": "Específico por especie",
            "dex-completion": "Completar Pokédex",
            "collectibles": "Coleccionables",
            "collectible": "Coleccionable",
            "event-items": "Objetos de evento",
            "gameplay": "Jugabilidad",
            "plates": "Placas",
            "apricorn-box": "Caja de Bayas",
            "data-cards": "Tarjetas datos",
            "jewels": "Joyas",
            "miracle-shooter": "Lanzador milagro",
            "pokeballs": "Poké Balls",
            "berries": "Bayas",
            "mail": "Cartas",
            "all-mail": "Todas las cartas",
            "battle": "Combate",
            "key": "Clave",
            "evolution": "Evolución",
            "spelunking": "Espeleología",
            "mulch": "Abono",
            "flutes": "Flautas",
            "unused": "No usado",
            "plot-advancement": "Avance de trama",
            "loot": "Botín",
            "other": "Otros",
            "dynamax-crystals": "Cristales Dinamax",
            "curry-ingredients": "Ingredientes curry",
            "nature-mints": "Menta naturaleza",
            "sandwich-ingredients": "Ingredientes sándwich",
            "tm-materials": "Materiales MT",
            "tera-shard": "Fragmento Tera",
            "species-candies": "Caramelos especie",
            "catching-bonus": "Bonus captura",
        }

   def pokemon_izenak_eskatu(self):
      try:
         response = requests.get(f"{self.base_url}pokemon?limit=1500", timeout=10)
         if response.status_code == 200:
            return response.json()['results']
         return []
      except Exception as e:
         print(f"Error en la lista de nombres: {e}")
         return []
   
   def pokemon_eskatu(self, izena):
    try:
        res_data = requests.get(f"{self.base_url}pokemon/{izena}", timeout=10)
        res_species = requests.get(f"{self.base_url}pokemon-species/{izena}", timeout=10)
        
        if res_data.status_code == 200 and res_species.status_code == 200:
            uneko_pokemon = res_data.json()
            espeziea = res_species.json()
            
            pre_eboluzioa = 0
            if espeziea.get("evolves_from_species") and espeziea.get("id", 0) < 10000:
                url = espeziea["evolves_from_species"]["url"]
                pre_eboluzioa = int(url.split('/')[-2])
                
            rate = espeziea.get('gender_rate', -1)
            generoa = 'Neutroa' if rate == -1 else 'Ar' if rate == 0 else 'Eme' if rate == 8 else 'Ar/Eme'
            
            irudia = uneko_pokemon['sprites']['other']['official-artwork']['front_default'] or uneko_pokemon['sprites']['front_default']
            
            gen_name = espeziea['generation']['name'].split('-')[1]
            generazioa = self.erromatarrak.get(gen_name, 0)
            
            return {
                "pokeId": uneko_pokemon['id'],
                "izena": uneko_pokemon['name'].capitalize(),
                "altuera": uneko_pokemon['height'],
                "pisua": uneko_pokemon['weight'],
                "generoa": generoa,
                "deskripzioa": self.__lortu_deskripzioa(espeziea),
                "irudia": irudia,
                "generazioa": generazioa,
                "pre_eboluzioa": pre_eboluzioa
            }
        return None
    except Exception as e:
        print(f"Error cargando pokemon {izena}: {e}")
        return None
   
   def mota_izenak_eskatu(self):
        try:
            response = requests.get(f"{self.base_url}type", timeout=10)
            if response.status_code == 200:
                return response.json()['results']
            return []
        except Exception as e:
            print(f"Error obteniendo nombres de tipos: {e}")
            return []
     
   def mota_eskatu(self, izena):
        try:
            response = requests.get(f"{self.base_url}type/{izena}", timeout=10)  
            if response.status_code == 200:
                mota = response.json()
                return {
                    "izena": izena,
                    "pokemonak": mota.get('pokemon', []),
                    "erlazioak": mota.get('damage_relations', {})
                }
            return None
        except Exception as e:
            print(f"Error cargando tipo {izena}: {e}")
            return None

   def mugimendu_izenak_eskatu(self):
        try:
            response = requests.get(f"{self.base_url}move?limit=1000", timeout=10)
            if response.status_code == 200:
                return response.json()['results']
            return []
        except Exception as e:
            print(f"Error obteniendo nombres de movimientos: {e}")
            return []
   
   def mugimendua_eskatu(self, izena):
        try:
            response = requests.get(f"{self.base_url}move/{izena}", timeout=10)
            if response.status_code == 200:
                mugimendua = response.json()
                return {
                    "izena": self.__lortu_izena(mugimendua).capitalize(),
                    "potentzia": mugimendua.get('power', 0),
                    "zehaztazuna": mugimendua.get('accuracy', 0),
                    "PP": mugimendua.get('pp', 0),
                    "efektua": self.__lortu_deskripzioa(mugimendua),
                    "pokemonMotaIzena": mugimendua['type']['name'].capitalize(),
                    "pokemonak": mugimendua.get('learned_by_pokemon', [])
                }
            return None
        except Exception as e:
            print(f"Error cargando movimiento {izena}: {e}")
            return None
   
   def abilezi_izenak_eskatu(self):
        try:
            response = requests.get(f"{self.base_url}ability?limit=500", timeout=10)
            if response.status_code == 200:
                return response.json()['results']
            return []
        except Exception as e:
            print(f"Error obteniendo nombres de habilidades: {e}")
            return []
   
   def abilezia_eskatu(self, izena):
        try:
            response = requests.get(f"{self.base_url}ability/{izena}", timeout=10)
            if response.status_code == 200:
                abilezia = response.json()
                return {
                    "izena": self.__lortu_izena(abilezia),
                    "deskripzioa": self.__lortu_deskripzioa(abilezia),
                    "pokemonak": abilezia.get('pokemon', [])
                }
            return None
        except Exception as e:
            print(f"Error cargando habilidad {izena}: {e}")
            return None

   def __lortu_izena(self, objektua):
        """Busca el nombre en español ('es') en la lista 'names'."""
        for sarrera in objektua.get('names', []):
            if sarrera['language']['name'] == 'es':
                return sarrera['name'].replace('\n', ' ').replace('\f', ' ')
        return objektua.get('name', '???')
   

   def __lortu_deskripzioa(self, objektua):
        """Filtra descripciones buscando el idioma español ('es')."""
        # 1. Comprobar flavor_text_entries (Pokémon, Species, Items)
        if 'flavor_text_entries' in objektua:
            for sarrera in objektua['flavor_text_entries']:
                if sarrera['language']['name'] == 'es':
                    # Algunos recursos usan 'flavor_text' y otros 'text'
                    texto = sarrera.get('flavor_text', sarrera.get('text', ''))
                    return texto.replace('\n', ' ').replace('\f', ' ')
        
        # 2. Comprobar effect_entries (Habilidades y Movimientos)
        if 'effect_entries' in objektua:
            for sarrera in objektua['effect_entries']:
                if sarrera['language']['name'] == 'es':
                    # Algunos recursos usan 'effect'
                    return sarrera.get('effect', '').replace('\n', ' ').replace('\f', ' ')

        return 'Descripción no disponible en español'

   # =====================================================
   # ITEMDEX
   # =====================================================

   # PokeAPI-tik item guztien izenak lortu
   # Zerrenda sinple bat bueltatu
   def item_izenak_eskatu(self):
       try:
           response = requests.get(f"{self.base_url}item?limit=4000", timeout=10)
           if response.status_code == 200:
               return response.json()['results']
           return []
       except Exception as e:
           print(f"Errorea lortzen itemaren izena: {e}")
           return []

   # Item baten datu osoak PokeAPI-tik lortu
   # Izena, deskripzioa eta mota bueltatu
   def itema_eskatu(self, izena):
       try:
           response = requests.get(f"{self.base_url}item/{izena}", timeout=10)
           if response.status_code != 200:
               return None

           item = response.json()

           # Izenak gaztelaniaz
           izena_es = self.__lortu_izena(item)

           # Deskripzioa gaztelaniaz
           deskr = self.__lortu_deskripzioa(item)

           # Mota
           mota_api = item.get('category', {}).get('name', 'other')
           mota = mota_api.replace("-", " ").title()

           # Itzulpena hiztegi propioarekin
           mota_limpia = mota_api.lower().strip()
           if mota_limpia in self.traducciones_tipos:
               mota = self.traducciones_tipos[mota_limpia]

           return {
               "id": item.get('id'),
               "izena": izena_es,
               "deskripzioa": deskr,
               "argazkia": item.get('sprites', {}).get('default'),
               "mota": mota
           }

       except Exception as e:
           print(f"Errorea itema kargatzen {izena}: {e}")
           return None

   def eboluzioak_eskatu(self):

       eboluzioKateak = []

       def get_id_from_url(url):
           if not url:
               return None
           return int(url.rstrip('/').split('/')[-1])

       def prozesatu_nodoa(nodoa, aurreko_id):
           if isinstance(nodoa, dict):
               species_url = nodoa.get("species", {}).get("url")
               evolves_to_list = nodoa.get("evolves_to", [])
           else:
               species_url = getattr(nodoa.species, 'url', None)
               evolves_to_list = getattr(nodoa, 'evolves_to', [])

           if not species_url:
               return

           uneko_id = get_id_from_url(species_url)

           if aurreko_id is not None:
               eboluzioKateak.append((aurreko_id, uneko_id))

           for eboluzioa in evolves_to_list:
               prozesatu_nodoa(eboluzioa, uneko_id)

       for i in range(1, 560):
           try:
               katea = pb.evolution_chain(i)
               if hasattr(katea, 'chain'):
                   prozesatu_nodoa(katea.chain, None)
               elif isinstance(katea, dict) and 'chain' in katea:
                   prozesatu_nodoa(katea['chain'], None)
           except:
               continue

       return eboluzioKateak

   def hartu_stats(self, id):
        uneko_pokemon = pb.pokemon(int(id))
        stats = {}
        for stat in uneko_pokemon.stats:
            stats[stat.stat.name] = stat.base_stat
        return stats
  
   def pokemon_izena_lortu(self, id):
        uneko_pokemon = pb.pokemon(int(id))
        return uneko_pokemon.name.capitalize()