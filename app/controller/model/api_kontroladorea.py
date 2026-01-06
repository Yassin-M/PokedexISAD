import pokebase as pb

class APIKontroladorea:

   def __init__(self):
      self.erromatarrak = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9}

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
      return pb.APIResourceList('pokemon')
   
   def pokemon_eskatu(self, izena):
      uneko_pokemon = pb.pokemon(izena)
      izen_erreala = uneko_pokemon.species.name
      espeziea = pb.pokemon_species(izen_erreala)
      generoa_rate = espeziea.gender_rate
      generoa = 'Neutroa' if generoa_rate == -1 else 'Ar' if generoa_rate == 0 else 'Eme' if generoa_rate == 8 else 'Ar/Eme'
      irudia = uneko_pokemon.sprites.other.official_artwork.front_default
      if not irudia:
         irudia = uneko_pokemon.sprites.front_default
      base_parametroak = {"pokeId": uneko_pokemon.id,
                           "izena": uneko_pokemon.name.capitalize(),
                           "altuera": uneko_pokemon.height,
                           "pisua": uneko_pokemon.weight,
                           "generoa": generoa,
                           "deskripzioa": self.__lortu_deskripzioa(espeziea),
                           "irudia": irudia,
                           "generazioa": self.erromatarrak.get(espeziea.generation.name.split('-')[1], 0)}
      return base_parametroak
   def mota_izenak_eskatu(self):
      return pb.APIResourceList('type')
     
   def mota_eskatu(self, izena):
      mota = pb.type_(izena)
      return {"izena": izena, "pokemonak": mota.pokemon, "erlazioak": mota.damage_relations}

   def mugimendu_izenak_eskatu(self):
      return pb.APIResourceList('move')
   
   def mugimendua_eskatu(self, izena):
      mugimendua = pb.move(izena)
      mugimendu_izena = self.__lortu_izena(mugimendua)
      mugimendu_efektua = self.__lortu_deskripzioa(mugimendua)
      parametroak = {"izena": mugimendu_izena.capitalize(), 
                     "potentzia": mugimendua.power, 
                     "zehaztazuna":mugimendua.accuracy, 
                     "PP": mugimendua.pp, 
                     "efektua": mugimendu_efektua, 
                     "pokemonMotaIzena":mugimendua.type.name.capitalize(),
                     "pokemonak": mugimendua.learned_by_pokemon
                  }
      return parametroak
   
   def abilezi_izenak_eskatu(self):
      return pb.APIResourceList('ability')
   
   def abilezia_eskatu(self, izena):
      abilezia = pb.ability(izena)
      abilezi_izena = abilezia.name
      for izena in abilezia.names:
            if izena.language.name == "es":
               abilezi_izena = izena.name
      deskripzioa = self.__lortu_deskripzioa(abilezia)
      parametroak = {"izena": abilezi_izena, "deskripzioa": deskripzioa, "pokemonak": abilezia.pokemon}
      return parametroak

   def __lortu_izena(self, objektua):
      for sarrera in objektua.names:
         if sarrera.language.name == 'es':
            return sarrera.name.replace('\n', ' ').replace('\f', ' ')
      return objektua.name
   

   def __lortu_deskripzioa(self, objektua):
      """Busca descripción en español adaptándose a si es Item o Pokémon"""
      if hasattr(objektua, 'flavor_text_entries'):
         for sarrera in objektua.flavor_text_entries:
            if sarrera.language.name == 'es':
               # Pokémon usa .flavor_text, los Items usan .text
               texto = getattr(sarrera, 'flavor_text', getattr(sarrera, 'text', ''))
               return texto.replace('\n', ' ').replace('\f', ' ')
      return 'Descripción no disponible en español'
   
   #itemdex

   def item_izenak_eskatu(self):
      return pb.APIResourceList("item")
   
   def itema_eskatu(self, izena_api):
        """Procesa un item: traduce nombre, descripción y categoría."""
        api_item = pb.item(izena_api)

        # 1. Nombre en español
        izena = None
        for n in api_item.names:
            if n.language.name == "es":
                izena = n.name
                break
        if not izena:
            izena = api_item.name.replace("-", " ").title()

        # 2. Descripción en español
        deskr = None
        for entry in api_item.flavor_text_entries:
            if entry.language.name == "es":
                deskr = entry.text.replace("\n", " ").replace("\f", " ")
                break
        if not deskr:
         deskr = "Descripción no disponible en español"

        # 3. Categoría (Tipo) en español
        mota_api = api_item.category.name
        mota = mota_api

        # Intento 1: Traducción oficial API
        for name in api_item.category.names:
            if name.language.name == "es":
                mota = name.name
                break

        # Intento 2: Fallback con diccionario propio si la API falla o devuelve inglés
        if mota == mota_api or mota.lower() == mota_api.lower():
            mota_limpia = mota_api.lower().strip()
            if mota_limpia in self.traducciones_tipos:
                mota = self.traducciones_tipos[mota_limpia]
            else:
                mota = mota_api.replace("-", " ").title()

        if not mota or mota.strip() == "":
            mota = "Otros"

        return {
            "id": api_item.id,
            "izena": izena,
            "deskripzioa": deskr,
            "argazkia": api_item.sprites.default,
            "mota": mota
        }

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