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
    harrapatuId INTEGER PRIMARY KEY AUTOINCREMENT,
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
    FOREIGN KEY (PokemonPokedexID) REFERENCES PokemonPokedex(pokeId),
    FOREIGN KEY (ErabiltzaileIzena) REFERENCES Erabiltzailea(izena)
);

CREATE TABLE IF NOT EXISTS Dauka (
    abileziIzena VARCHAR(25),
    harrapatuId VARCHAR(25),
    PRIMARY KEY (abileziIzena, harrapatuId),
    FOREIGN KEY (abileziIzena) REFERENCES Abilezia(izena),
    FOREIGN KEY (harrapatuId) REFERENCES PokemonTalde(harrapatuId)
);

CREATE TABLE IF NOT EXISTS JarraitzenDu (
    JarraitzaileIzena VARCHAR(25),
    JarraituIzena VARCHAR(25),
    Notifikatu BOOLEAN default TRUE,
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
    harrapatuId INT,
    mugimenduIzena VARCHAR(25),
    PRIMARY KEY (harrapatuId, mugimenduIzena),
    FOREIGN KEY (harrapatuId) REFERENCES PokemonTalde(harrapatuId),
    FOREIGN KEY (mugimenduIzena) REFERENCES Mugimendua(izena)
);

CREATE TABLE IF NOT EXISTS IzanDezake (
    pokemonPokedexID INT,
    izena VARCHAR(25),
    ezkutua BOOLEAN,
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
    harrapatuId INT,
    erabiltzaileIzena VARCHAR(25),
    PRIMARY KEY (taldeIzena, harrapatuId, erabiltzaileIzena),
    FOREIGN KEY (taldeIzena, erabiltzaileIzena) REFERENCES Taldea(taldeIzena, erabiltzaileIzena),
    FOREIGN KEY (harrapatuId) REFERENCES PokemonTalde(harrapatuId)
);