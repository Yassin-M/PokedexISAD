CREATE TABLE IF NOT EXISTS Erabiltzailea (
    izena VARCHAR(45), 
    pasahitza VARCHAR(255), 
    email VARCHAR(255),
    jaiotze_data DATE,
    rola VARCHAR(15),
    PRIMARY KEY (izena)
);

CREATE TABLE IF NOT EXISTS PokemonPokedex (
    pokeId INT,
    izena VARCHAR(45),
    altuera FLOAT,
    pisua FLOAT,
    generoa VARCHAR(20),
    deskripzioa TEXT,
    irudia VARCHAR(255),
    generazioa INT,
    PRIMARY KEY (pokeId)
);

CREATE TABLE IF NOT EXISTS Abilezia (
    izena VARCHAR(25),
    deskripzioa TEXT,
    PRIMARY KEY (izena)
);

CREATE TABLE IF NOT EXISTS MotaPokemon (
    pokemonMotaIzena VARCHAR(15),
    irudia VARCHAR(255),
    PRIMARY KEY (pokemonMotaIzena)
);

CREATE TABLE IF NOT EXISTS MotaItem (
    ItemMotaIzena VARCHAR(25),
    PRIMARY KEY (ItemMotaIzena)
);

CREATE TABLE IF NOT EXISTS Item (
    itemID INT,
    izena VARCHAR(25),
    deskripzioa TEXT,
    argazkia VARCHAR(255),
    MotaIzena VARCHAR(25),
    PRIMARY KEY (itemID),
    FOREIGN KEY (MotaIzena) REFERENCES MotaItem(ItemMotaIzena)
);

CREATE TABLE IF NOT EXISTS Multiplikatzailea (
    pokemonMotaJaso VARCHAR(15),
    pokemonMotaEraso VARCHAR(15),
    multiplikatzailea FLOAT,
    PRIMARY KEY (pokemonMotaJaso, pokemonMotaEraso),
    FOREIGN KEY (pokemonMotaJaso) REFERENCES MotaPokemon(pokemonMotaIzena),
    FOREIGN KEY (pokemonMotaEraso) REFERENCES MotaPokemon(pokemonMotaIzena)
);

CREATE TABLE IF NOT EXISTS DaMotaPokemon (
    motaIzena VARCHAR(15),
    pokemonID INT,
    PRIMARY KEY (motaIzena, pokemonID),
    FOREIGN KEY (motaIzena) REFERENCES MotaPokemon(pokemonMotaIzena),
    FOREIGN KEY (pokemonID) REFERENCES PokemonPokedex(pokeId)
);

CREATE TABLE IF NOT EXISTS Eboluzioa (
    pokemonPokedexID INT,
    eboluzioaPokeId INT,
    PRIMARY KEY (pokemonPokedexID, eboluzioaPokeId),
    FOREIGN KEY (pokemonPokedexID) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (eboluzioaPokeId) REFERENCES PokemonPokedex(pokeId)
);

CREATE TABLE IF NOT EXISTS PokemonTalde (
    izena VARCHAR(25),
    maila INT,
    adiskidetasun_maila INT,
    generoa VARCHAR(10),
    HP INT,
    ATK INT,
    SPATK INT,
    DEF INT,
    SPDEF INT,
    SPE INT,
    PokemonPokedexID INT,
    ErabiltzaileIzena VARCHAR(25),
    PRIMARY KEY (izena),
    FOREIGN KEY (PokemonPokedexID) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (ErabiltzaileIzena) REFERENCES Erabiltzailea(izena)
);

CREATE TABLE IF NOT EXISTS Dauka (
    abileziIzena VARCHAR(25),
    pokemonIzena VARCHAR(25),
    PRIMARY KEY (abileziIzena, pokemonIzena),
    FOREIGN KEY (abileziIzena) REFERENCES Abilezia(izena),
    FOREIGN KEY (pokemonIzena) REFERENCES PokemonTalde(izena)
);

CREATE TABLE IF NOT EXISTS JarraitzenDu (
    JarraitzaileIzena VARCHAR(25),
    JarraituIzena VARCHAR(25),
    PRIMARY KEY (JarraitzaileIzena, JarraituIzena),
    FOREIGN KEY (JarraitzaileIzena) REFERENCES Erabiltzailea(izena),
    FOREIGN KEY (JarraituIzena) REFERENCES Erabiltzailea(izena)
);

CREATE TABLE IF NOT EXISTS Notifikatu (
    DataOrdua DATETIME,
    ErabiltzaileIzena VARCHAR(25),
    deskripzioa TEXT,
    PRIMARY KEY (DataOrdua, ErabiltzaileIzena),
    FOREIGN KEY (ErabiltzaileIzena) REFERENCES Erabiltzailea(izena)
);

CREATE TABLE IF NOT EXISTS Mugimendua (
    izena VARCHAR(25),
    potentzia INT,
    zehaztazuna INT,
    PP INT,
    efektua TEXT,
    pokemonMotaIzena VARCHAR(25),
    PRIMARY KEY (izena),
    FOREIGN KEY (pokemonMotaIzena) REFERENCES MotaPokemon(pokemonMotaIzena)
);

CREATE TABLE IF NOT EXISTS MugimenduIzanTalde (
    pokemonID INT,
    mugimenduIzena VARCHAR(25),
    PRIMARY KEY (pokemonID, mugimenduIzena),
    FOREIGN KEY (pokemonID) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (mugimenduIzena) REFERENCES Mugimendua(izena)
);

CREATE TABLE IF NOT EXISTS IzanDezake (
    pokemonPokedexID INT,
    izena VARCHAR(25),
    ezkutua VARCHAR(25),
    PRIMARY KEY (pokemonPokedexID, izena),
    FOREIGN KEY (pokemonPokedexID) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (izena) REFERENCES Abilezia(izena)
);

CREATE TABLE IF NOT EXISTS IkasDezake (
    pokedexId INT,
    mugiIzena VARCHAR(25),
    PRIMARY KEY (pokedexId, mugiIzena),
    FOREIGN KEY (pokedexId) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (mugiIzena) REFERENCES Mugimendua(izena)
);

CREATE TABLE IF NOT EXISTS Taldea (
    taldeIzena VARCHAR(25),
    erabiltzaileIzena VARCHAR(25),
    PRIMARY KEY (taldeIzena),
    FOREIGN KEY (erabiltzaileIzena) REFERENCES Erabiltzailea(izena)
);

CREATE TABLE IF NOT EXISTS PokemonTaldean (
    taldeIzena VARCHAR(25),
    pokeId INT,
    PRIMARY KEY (taldeIzena, pokeId),
    FOREIGN KEY (taldeIzena) REFERENCES Taldea(taldeIzena),
    FOREIGN KEY (pokeId) REFERENCES PokemonPokedex(pokeId)
);

-- 1. Borrar Notificaciones de estos 4
DELETE FROM Notifikatu 
WHERE ErabiltzaileIzena IN ('Ash', 'Misty', 'Brock', 'Gary');

-- 2. Borrar Relaciones de seguir
DELETE FROM JarraitzenDu 
WHERE JarraitzaileIzena IN ('Ash', 'Misty', 'Brock', 'Gary')
   OR JarraituIzena IN ('Ash', 'Misty', 'Brock', 'Gary');

-- 3. Borrar Usuarios
DELETE FROM Erabiltzailea 
WHERE Izena IN ('Ash', 'Misty', 'Brock', 'Gary');