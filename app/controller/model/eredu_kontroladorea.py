import random
import pokebase as pb
from app.database import db

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
      sql2 = "SELECT PT.harrapatuId, PP.irudia FROM Taldea T JOIN PokemonTaldean PT  ON T.taldeIzena = PT.taldeIzena JOIN PokemonTalde PKT ON PT.harrapatuId = PKT.harrapatuId JOIN PokemonPokedex PP ON PKT.PokemonPokedexID = PP.pokeId WHERE T.erabiltzaileIzena = ? AND T.taldeIzena = ?"
      taldea = self.db.select(sql2, (erabiltzailea, taldeIzena))

      json5 = [ {'pokeID': pokeID, 'argazkia': irudia} for (pokeID, irudia) in taldea ]
      return json5
    
    def sartu_taldera(self, taldeIzena, erabiltzailea, pokemonId):
      sql3 = "SELECT COUNT(*) as count FROM PokemonTaldean PT JOIN Taldea T ON PT.taldeIzena = T.taldeIzena WHERE T.erabiltzaileIzena = ? AND T.taldeIzena = ?"
      count_result = self.db.select(sql3, (erabiltzailea, taldeIzena))
      if count_result and count_result[0]['count'] >= 6:
          raise ValueError("Ezin dira 6 pokémon baino gehiago sartu talde batean")

      try:
          p_api = pb.pokemon(int(pokemonId))
          stats = {s.stat.name: s.base_stat for s in p_api.stats}

          hp = int(stats.get('hp', 40) * 2)
          atk = int(stats.get('attack', 40) * 1.5)
          spatk = int(stats.get('special-attack', 40) * 1.5)
          def_ = int(stats.get('defense', 40) * 1.5)
          spdef = int(stats.get('special-defense', 40) * 1.5)
          spe = int(stats.get('speed', 40) * 1.5)
          izena = p_api.name.capitalize()
          
          generoa = random.choice(['Ar', 'Eme', 'Neutroa'])

          sql_insert_instance = """
                INSERT INTO PokemonTalde 
                (izena, maila, adiskidetasun_maila, generoa, HP, ATK, SPATK, DEF, SPDEF, SPE, PokemonPokedexID, ErabiltzaileIzena) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Defektuz maila 50 eta adiskidetasuna 0 jarri dugu
          self.db.insert(sql_insert_instance, (izena, 50, 0, generoa, hp, atk, spatk, def_, spdef, spe, pokemonId, erabiltzailea))

      except Exception as e:
          print(f"Errorea API deian edo txertatzean: {e}")
            # APIak huts egiten badu, balio lehenetsiekin sartu
          sql_fallback = "INSERT INTO PokemonTalde (izena, maila, PokemonPokedexID, ErabiltzaileIzena) VALUES (?, 50, ?, ?)"
          self.db.insert(sql_fallback, ("Pokemon", pokemonId, erabiltzailea))

        # 4. ID-A LORTU (Auto Increment)
        # Azken harrapatuId-a lortu behar dugu abileziak eta mugimenduak lotzeko
        # Oharra: Hau DB kudeatzailearen arabera alda daiteke, baina SQLite-n orokorrean MAX(id) funtzionatzen du testuinguru honetan
      sql_last_id = "SELECT MAX(harrapatuId) as id FROM PokemonTalde WHERE ErabiltzaileIzena = ? AND PokemonPokedexID = ?"
      res_id = self.db.select(sql_last_id, (erabiltzailea, pokemonId))
      harrapatu_id = res_id[0]['id'] if res_id and res_id[0]['id'] else None
      print(harrapatu_id)

      if harrapatu_id:
          # 5. ABILEZIA (DAUKA TAULA)
          # Pokemon horrek izan ditzakeen abileziak lortu
          sql_abis = "SELECT izena FROM IzanDezake WHERE pokemonPokedexID = ?"
          posibleak = self.db.select(sql_abis, (pokemonId,))
          
          if posibleak:
              # Bat ausaz aukeratu
              aukeratua = random.choice(posibleak)
              if isinstance(aukeratua, dict): 
                  aukeratua_izena = aukeratua['izena']
              else:
                  aukeratua_izena = aukeratua[0] # Tupla bada

              # KONTUZ: Schema.sql-an 'harraptuId' jartzen du (typo), ez 'harrapatuId'
              sql_dauka = "INSERT INTO Dauka (abileziIzena, harrapatuId) VALUES (?, ?)"
              self.db.insert(sql_dauka, (aukeratua_izena, harrapatu_id))

          # 6. MUGIMENDUAK (MUGIMENDUIZANTALDE TAULA)
          # Pokemon horrek ikas ditzakeen mugimenduak lortu
          sql_moves = "SELECT mugiIzena FROM IkasDezake WHERE pokedexId = ?"
          moves_posibleak = self.db.select(sql_moves, (pokemonId,))
          
          move_list = []
          for m in moves_posibleak:
                if isinstance(m, dict):
                    move_list.append(m['mugiIzena'])
                else:
                    move_list.append(m[0])

          # 4 ausaz aukeratu (edo gutxiago badaude, denak)
          num_moves = min(len(move_list), 4)
          chosen_moves = random.sample(move_list, num_moves)

          sql_move_insert = "INSERT INTO MugimenduIzanTalde (harrapatuId, mugimenduIzena) VALUES (?, ?)"
          for move in chosen_moves:
              self.db.insert(sql_move_insert, (harrapatu_id, move))
      
      sql4 = "INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena) VALUES (?, ?, ?)"
      self.db.insert(sql4, (taldeIzena, harrapatu_id, erabiltzailea))

      sql6 = "SELECT izena FROM PokemonTalde WHERE harrapatuId = ?"
      izena = self.db.select(sql6, (harrapatu_id,))
      return izena[0]['izena']



    def ezabatu_taldetik(self, taldeIzena, erabiltzailea, pokemonId):
        # Delete movements associated with the Pokémon in the team

        sql6 = "SELECT izena FROM PokemonTalde WHERE harrapatuId = ?"
        izena = self.db.select(sql6, (pokemonId,))
        pokeIzena = izena[0]['izena']
        
        sql_delete_moves = "DELETE FROM MugimenduIzanTalde WHERE harrapatuId = ?"
        self.db.delete(sql_delete_moves, (pokemonId,))

        # Delete abilities associated with the Pokémon in the team
        sql_delete_ability = "DELETE FROM Dauka WHERE harrapatuId = ?"
        self.db.delete(sql_delete_ability, (pokemonId,))

        # Delete the Pokémon from the team
        sql_delete_pokemon_team = "DELETE FROM PokemonTaldean WHERE harrapatuId = ? AND taldeIzena = ? AND erabiltzaileIzena = ?"
        self.db.delete(sql_delete_pokemon_team, (pokemonId, taldeIzena, erabiltzailea))

        # Delete the Pokémon from the PokemonTalde table
        sql_delete_pokemon = "DELETE FROM PokemonTalde WHERE harrapatuId = ?"
        self.db.delete(sql_delete_pokemon, (pokemonId,))

        return pokeIzena


    def ezabatu_taldea(self, taldeIzena, erabiltzailea):
        # Get all Pokémon IDs in the team
        sql_get_pokemon_ids = "SELECT harrapatuId FROM PokemonTaldean WHERE taldeIzena = ? AND erabiltzaileIzena = ?"
        pokemon_ids = self.db.select(sql_get_pokemon_ids, (taldeIzena, erabiltzailea))

        # Delete movements, abilities, and Pokémon for each Pokémon in the team
        for pokemon in pokemon_ids:
            pokemonId = pokemon['harrapatuId']

            # Delete movements associated with the Pokémon
            sql_delete_moves = "DELETE FROM MugimenduIzanTalde WHERE harrapatuId = ?"
            self.db.delete(sql_delete_moves, (pokemonId,))

            # Delete abilities associated with the Pokémon
            sql_delete_ability = "DELETE FROM Dauka WHERE harrapatuId = ?"
            self.db.delete(sql_delete_ability, (pokemonId,))

            # Delete the Pokémon from the PokemonTalde table
            sql_delete_pokemon = "DELETE FROM PokemonTalde WHERE harrapatuId = ?"
            self.db.delete(sql_delete_pokemon, (pokemonId,))

        # Delete all Pokémon from the team
        sql_delete_pokemon_team = "DELETE FROM PokemonTaldean WHERE taldeIzena = ? AND erabiltzaileIzena = ?"
        self.db.delete(sql_delete_pokemon_team, (taldeIzena, erabiltzailea))

        # Delete the team itself
        sql_delete_team = "DELETE FROM Taldea WHERE taldeIzena = ? AND erabiltzaileIzena = ?"
        self.db.delete(sql_delete_team, (taldeIzena, erabiltzailea))
      
    def bistaratu_pokemon_taldea(self, pokeId):
      sql2 = "SELECT P.harrapatuId, P.izena, P.HP, P.ATK, P.SPATK, P.DEF, P.SPDEF, P.SPE, PP.irudia, PP.pokeId, PP.pisua, PP.altuera FROM PokemonTalde P, PokemonPokedex PP WHERE P.harrapatuId = ? AND P.PokemonPokedexID = PP.pokeId"
      pokemon = self.db.select(sql2, (pokeId,))
        
      for pokemons in pokemon:
        json3 = {
            'harrapatuId': pokemons['harrapatuId'],
            'izena': pokemons['izena'],         
            'argazkia': pokemons['irudia'],
            'id': pokemons['pokeId'],
            'pisua': pokemons['altuera'],
            'altuera': pokemons['pisua']
        }

      stats = {
        'hp': pokemons['HP'],
        'atk': pokemons['ATK'],
        'spatk': pokemons['SPATK'],
        'def': pokemons['DEF'],
        'spdef': pokemons['SPDEF'],
        'spe': pokemons['SPE'],
      }

      json3['stats'] = stats
      abilezia = self.db.select("SELECT abileziIzena FROM Dauka WHERE harrapatuId = ?", [json3['harrapatuId']])
      abIzena = [abi['abileziIzena'] for abi in abilezia]
      json3['abileziak'] = abIzena
      mugimenduak = self.db.select("SELECT mugimenduIzena FROM MugimenduIzanTalde WHERE harrapatuId = ?", [json3['harrapatuId']])
      mugiIzenak = [mugi['mugimenduIzena'] for mugi in mugimenduak]
      json3['mugimenduak'] = mugiIzenak
      return json3 



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
        print(id)
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
    
    def notifikazioBerria(ErabiltzaileIzena, DataOrdua, deskripzioa):
      query = "INSERT INTO Notifikatu (ErabiltzaileIzena, deskripzioa, DataOrdua) VALUES (?, ?, ?)"
      db.insert(ErabiltzaileIzena, deskripzioa, DataOrdua)
      return