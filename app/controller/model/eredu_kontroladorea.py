import pokebase as pb

class EreduKontroladorea:
   #metodos
   def __init__(self, db):
      self.db = db

   def pokedex_kargatu(self, JSON2):
      if not self.pokemonak_konprobatu():
         self.pokemonak_kargatu()
      if not self.motak_konprobatu():
         self.motak_kargatu()
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

      return self.db.select(sql3, parametroak)

   def pokemonak_konprobatu(self):
      return len(self.db.select("SELECT * FROM PokemonPokedex"))>1
   
   def motak_konprobatu(self):
      return len(self.db.select("SELECT * FROM MotaPokemon"))>1 and len(self.db.select("SELECT * FROM DaMotaPokemon"))>1 and len(self.db.select("SELECT * FROM Multiplikatzailea"))

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
                                self.__lortu_pokedex_deskripzioa(espeziea), 
                                irudia, 
                                erromatarrak.get(espeziea.generation.name.split('-')[1], 0)]
            self.db.insert(sql2, base_parametroak)
         except Exception as e:
            print(f"Error {e}")

   
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
                  pokemon_id = pb.pokemon(pokemon.pokemon.name).id
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

   def mugimenduak_kargatu(self):
      pass
          

   def __lortu_pokedex_deskripzioa(self, espeziea):
      for sarrera in espeziea.flavor_text_entries:
         if sarrera.language.name == 'es':
            return sarrera.flavor_text.replace('\n', ' ').replace('\f', ' ')
      return 'Ez dago deskripziorik gaztelaniaz'
