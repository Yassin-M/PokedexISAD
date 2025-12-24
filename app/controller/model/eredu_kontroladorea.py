class EreduKontroladorea:

   #metodos
   def __init__(self, db):
      self.db = db

   
   def pokemonak_kargatu(self):
      sql2 = 'INSERT INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa) VALUES (?, ?, ?, ?, ?, ?)'
      for pokemon in pb.APIResourceList('pokemon'):
         uneko_pokemon = pb.pokemon(pokemon.name)
         deskr = self.__lortu_pokedex_deskripzioa(pb.pokemon_species(pokemon.name))
         base_parametroak = [uneko_pokemon.id, uneko_pokemon.name, uneko_pokemon.height, uneko_pokemon.weight]
         generoa = pb.pokemon_species(pokemon.name).gender_rate
         generoak = []

         if generoa == -1:
            generoak = ['Neutroa']
         elif generoa == 0:
            generoak = ['Ar']
         elif generoa == 8:
            generoak = ['Eme']
         else:
            generoak = ['Ar', 'Eme']

         for g in generoak:
            parameters = base_parametroak + [g, deskr]
            self.db.insert(sql2, parameters)

   def __lortu_pokedex_deskripzioa(self, espeziea):
      for sarrera in espeziea.flavor_text_entries:
         if sarrera.language_name == 'es':
            return sarrera.flavor_text.replace('\n', ' ').replace('\f', ' ')
      return 'Ez dago deskripziorik gaztelaniaz'
