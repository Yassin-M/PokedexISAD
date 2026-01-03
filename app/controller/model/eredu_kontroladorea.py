import pokebase as pb

class EreduKontroladorea:

    def __init__(self, db):
        self.db = db

    def taldeak_kargatu(self, erabiltzailea):
      sql1 = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeak = self.db.select(sql1, (erabiltzailea,))

      json4 = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
      return json4
    
    def sortu_taldea_hutsa(self, erabiltzailea):
      sql = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeKop = self.db.select(sql, (erabiltzailea,))

      zenbakiak = set()
      for (izena,) in taldeKop:
        if izena.startswith("Talde "):
              try:
                zenb = int(izena.split(" ")[1])
                zenbakiak.add(zenb)
              except ValueError:
                  pass

      if len(zenbakiak) >= 10:      
        raise ValueError("Ezin dira 10 talde baino gehiago eduki")
      else:
        i = 1
        while i in zenbakiak:
          i += 1

        taldeIzena = f"Talde {i}"
        sql2 = " INSERT INTO taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)"
        self.db.insert(sql2, (taldeIzena, erabiltzailea))
        return taldeIzena
    
    def get_taldea(self, taldeIzena, erabiltzailea):
      sql2 = "SELECT PT.pokeID, PP.irudia FROM Taldea T JOIN PokemonTaldean PT  ON T.taldeIzena = PT.taldeIzena JOIN PokemonPokedex PP ON PT.pokeId = PP.pokeId WHERE erabiltzaileIzena = ? AND T.taldeIzena = ?"
      taldea = self.db.select(sql2, (erabiltzailea, taldeIzena))

      json5 = [ {'pokeID': pokeID, 'argazkia': irudia} for (pokeID, irudia) in taldea ]
      return json5
    
    def pokedex_kargatu(self, JSON2):
      if not self.pokemonak_konprobatu():
         self.pokemonak_kargatu()
      if not self.motak_konprobatu():
         self.motak_kargatu()
      if not self.abileziak_konprobatu():
         self.abileziak_kargatu()
      if not self.mugimenduak_konprobatu():
         self.mugimenduak_kargatu()
      sql3 = "SELECT P.izena, P.irudia, P.pokeId FROM PokemonPokedex P"
      parametroak = []

      if JSON2['motak']:
         sql3 += " JOIN DaMotaPokemon DM ON P.pokeId = DM.pokemonID JOIN MotaPokemon M ON DM.motaIzena = M.pokemonMotaIzena"

      if JSON2['izena']:
         sql3 += " WHERE P.izena LIKE ?"
         parametroak.append(f"%{JSON2['izena']}%") 

      if JSON2['generazioak']:
         signos = ','.join(['?'] * len(JSON2['generazioak']))
         operator = "AND" if "WHERE" in sql3 else "WHERE"
         sql3 += f" {operator} P.generazioa IN ({signos})"
         parametroak.extend(JSON2['generazioak'])

      if JSON2['motak']:
         signos_motak = ','.join(['?'] * len(JSON2['motak']))
         operador = "AND" if "WHERE" in sql3 else "WHERE"
         sql3 += f" {operador} M.pokemonMotaIzena IN ({signos_motak})"
         parametroak.extend(JSON2['motak'])

      errenkadak = self.db.select(sql3, parametroak)

      json1 = []

      for pokemon in errenkadak:
         datuak = {
            'izena': pokemon['izena'],
            'argazkia': pokemon['irudia'],
            'id': pokemon['pokeId']
         }
         json1.append(datuak)
      
      return json1

    def pokemonak_kargatu(self):
        sql2 = 'INSERT OR IGNORE INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa, irudia, generazioa) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        i = 0
        erromatarrak = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9} # para conseguir el numero de la generacion (la api lo devuelve como "generation-xx")
        for pokemon in pb.APIResourceList('pokemon'):
          try:
              uneko_pokemon = pb.pokemon(pokemon['name'])
              izen_erreala = uneko_pokemon.species.name
              espeziea = pb.pokemon_species(izen_erreala)
              generoa_rate = espeziea.gender_rate
              generoa = 'Neutroa' if generoa_rate == -1 else 'Ar' if generoa_rate == 0 else 'Eme' if generoa_rate == 8 else 'Ar/Eme'
              irudia = uneko_pokemon.sprites.other.official_artwork.front_default
              if not irudia:
                irudia = uneko_pokemon.sprites.front_default
              base_parametroak = [uneko_pokemon.id, 
                                  uneko_pokemon.name.capitalize(), 
                                  uneko_pokemon.height, 
                                  uneko_pokemon.weight, 
                                  generoa, 
                                  self.__lortu_deskripzioa(espeziea), 
                                  irudia, 
                                  erromatarrak.get(espeziea.generation.name.split('-')[1], 0)]
              self.db.insert(sql2, base_parametroak)
          except Exception as e:
              print(f"Error {e}")

    def bistaratu_pokemon(self, id):
        sql = "SELECT P.izena, P.pokeId, P.irudia, P.deskripzioa, P.pisua, P.altuera FROM PokemonPokedex P WHERE P.pokeId = ?"
        errenkada = self.db.select(sql, [id])[0]
        
        if errenkada:
          json3 = {
              'izena': errenkada['izena'],
              'argazkia': errenkada['irudia'],
              'deskr': errenkada['deskripzioa'],
              'id': errenkada['pokeId'],
              'altuera': errenkada['altuera'],
              'pisua': errenkada['pisua']
          }
          abileziak = self.db.select("SELECT izena FROM IzanDezake WHERE pokemonPokedexID = ?", [errenkada['pokeId']])
          izenak = [abi['izena'] for abi in abileziak]
          json3['abileziak'] = izenak
          return json3 
    
    def motak_kargatu(self):
        sql1 = "INSERT INTO MotaPokemon (pokemonMotaIzena) VALUES (?)"
        sql2 = "INSERT INTO DaMotaPokemon (motaIzena, pokemonID) VALUES (?, ?)"
        for mota in pb.APIResourceList('type'):
          try:
              if mota['name'] in ['unknown', 'shadow']:
                    continue
              self.db.insert(sql1, [mota['name']])
              tipo = pb.type_(mota['name'])
              for pokemon in tipo.pokemon:
                try:
                    pokemon_id = int(pokemon.pokemon.url.split('/')[-2])
                    self.db.insert(sql2, [mota['name'], pokemon_id])
                except Exception as e:
                    print(f"Error {e}")
          except Exception as e:
              print(f"Error {e}")

        sql3 = "INSERT INTO Multiplikatzailea(pokemonMotaJaso, pokemonMotaEraso, multiplikatzailea) VALUES (?, ?, ?)"
        for mota in pb.APIResourceList('type'):
          tipo = pb.type_(mota['name'])
          dobles = tipo.damage_relations.double_damage_to
          mitades = tipo.damage_relations.half_damage_to
          zeros = tipo.damage_relations.no_damage_to
          for doble in dobles:
              parametroak = [doble.name, mota['name'], 2.0]
              self.db.insert(sql3, parametroak)
          for mitad in mitades:
              parametroak = [mitad.name, mota['name'], 0.5]
              self.db.insert(sql3, parametroak)
          for zero in zeros:
              parametroak = [zero.name, mota['name'], 0.0]
              self.db.insert(sql3, parametroak)
          #esta parte habra que ver como acortarla un poco

    def abileziak_kargatu(self):
        sql1 = "INSERT OR IGNORE INTO Abilezia (izena, deskripzioa) VALUES (?, ?)"
        sql2 = "INSERT OR IGNORE INTO IzanDezake (pokemonPokedexID, izena, ezkutua) VALUES (?, ?, ?)"
        for abileziak in pb.APIResourceList('ability'):
          abilezia = pb.ability(abileziak['name'])
          abilezi_izena = abilezia.name
          for izena in abilezia.names:
              if izena.language.name == "es":
                abilezi_izena = izena.name
          deskripzioa = self.__lortu_deskripzioa(abilezia)
          self.db.insert(sql1, [abilezi_izena, deskripzioa])
          for pokemon in abilezia.pokemon:
              poke_id = int(pokemon.pokemon.url.split('/')[-2])
              self.db.insert(sql2, [poke_id, abilezi_izena, pokemon.is_hidden])
    
    def mugimenduak_kargatu(self):
        sql1 = "INSERT INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) VALUES (?, ?, ?, ?, ?, ?)"
        sql2 = "INSERT INTO IkasDezake (pokedexId, mugiIzena) VALUES (?, ?)"
        for izena in pb.APIResourceList('move'):
          mugimendua = pb.move(izena['name'])
          mugimendu_izena = self.__lortu_izena(mugimendua)
          mugimendu_efektua = self.__lortu_deskripzioa(mugimendua)
          parametroak = [mugimendu_izena.capitalize(), mugimendua.power, mugimendua.accuracy, mugimendua.pp, mugimendu_efektua, mugimendua.type.name]
          self.db.insert(sql1, parametroak)
          for pokemon in mugimendua.learned_by_pokemon:
              pokemon_id = int(pokemon.url.split('/')[-2])
              self.db.insert(sql2, [pokemon_id, mugimendu_izena])
          
    def __lortu_deskripzioa(self, objektua):
        for sarrera in objektua.flavor_text_entries:
          if sarrera.language.name == 'es':
              return sarrera.flavor_text.replace('\n', ' ').replace('\f', ' ')
        return 'Ez dago deskripziorik gaztelaniaz'
    
    def __lortu_izena(self, objektua):
        for sarrera in objektua.names:
          if sarrera.language.name == 'es':
              return sarrera.name.replace('\n', ' ').replace('\f', ' ')
        return objektua.name

    def pokemonak_konprobatu(self):
        return len(self.db.select("SELECT * FROM PokemonPokedex"))>1
    
    def motak_konprobatu(self):
        return len(self.db.select("SELECT * FROM MotaPokemon"))>1 and len(self.db.select("SELECT * FROM DaMotaPokemon"))>1 and len(self.db.select("SELECT * FROM Multiplikatzailea"))
    
    def mugimenduak_konprobatu(self):
        return len(self.db.select("SELECT * FROM Mugimendua"))>0

    def abileziak_konprobatu(self):
        hay_defs = len(self.db.select("SELECT izena FROM Abilezia LIMIT 1")) > 0

        hay_relaciones = len(self.db.select("SELECT pokemonPokedexID FROM IzanDezake LIMIT 1")) > 0

        return hay_defs and hay_relaciones