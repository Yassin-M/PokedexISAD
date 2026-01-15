# app/test/conftest.py
import pytest

@pytest.fixture()
def app():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def logged_in_client(client):
    """Saioa hasita dagoen bezeroa"""
    # Erabiltzailea erregistratu
    username = "test_user"
    test_data = {
        'erabiltzailea': username,
        'email': f'{username}@example.com',
        'jaiotze_data': '2000-01-01',
        'pasahitza': 'TestPass123!',
        'pasahitza_berretsi': 'TestPass123!'
    }

    client.post('/register', data=test_data, follow_redirects=True)

    # Saioa hasi
    client.post('/login', data={
        'erabiltzailea': username,
        'password': 'TestPass123!'
    }, follow_redirects=True)

    return client

@pytest.fixture()
def onenak_test_data(app):
    """
    Probako erabiltzailea, taldea eta Pokémon datuak sortzen ditu
    /chatbot/onenak probetarako.
    Proba amaitu ondoren, datuak automatikoki garbitzen dira.
    """
    from app.database.database import Connection

    conn = Connection()
    erabiltzaileIzena = "test_user"
    taldeIzena = "MY_TEST_TEAM"

    # --- 1. Erabiltzailea sortu edo existitzen bada ezabatzea ---
    conn.insert(
        "INSERT OR IGNORE INTO Erabiltzailea (izena) VALUES (?)",
        (erabiltzaileIzena,)
    )

    # --- 2. Taldea sortu ---
    conn.insert(
        "INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)",
        (taldeIzena, erabiltzaileIzena)
    )

    # --- 3. 4 Pokémon Pokedex aukeratu ---
    pokemons = conn.select(
        "SELECT pokeId, izena FROM PokemonPokedex ORDER BY pokeId LIMIT 5",
        ()
    )

    # --- 5. Pokemon estatistikak ---
    stat_sets = [
        (50, 50, 50, 50, 50, 50),
        (60, 60, 60, 60, 60, 60),
        (70, 70, 70, 70, 70, 70),
        (80, 80, 80, 80, 80, 80),
        (100, 100, 100, 100, 100, 100)
    ]

    inserted_harrapatuIds = []

    for i, pokemon in enumerate(pokemons):
        hp, atk, spatk, defense, spdef, spe = stat_sets[i]
        izena = f"{pokemon['izena']}_test_{i+1}"

        # --- 6. Pokemon taldean sartu ---
        conn.insert(
            """
            INSERT INTO PokemonTalde
            (izena, maila, adiskidetasun_maila, generoa,
             HP, ATK, SPATK, DEF, SPDEF, SPE,
             PokemonPokedexID, ErabiltzaileIzena)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                izena,
                50,
                70,
                ['Ar', 'Eme', 'Neutroa'][i % 3],
                hp, atk, spatk, defense, spdef, spe,
                pokemon['pokeId'],
                erabiltzaileIzena
            )
        )
        # --- 7. harrapatuId lortu ---
        harrapatu = conn.select(
            """
            SELECT harrapatuId
            FROM PokemonTalde
            WHERE izena = ? AND ErabiltzaileIzena = ?
            ORDER BY harrapatuId DESC
            LIMIT 1
            """,
            (izena, erabiltzaileIzena)
        )[0]["harrapatuId"]

        inserted_harrapatuIds.append(harrapatu)
        # --- 8. PokemonTaldean sartu ---
        conn.insert(
            """
            INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena)
            VALUES (?, ?, ?)
            """,
            (taldeIzena, harrapatu, erabiltzaileIzena)
        )

    # ----------------- Proba exekutatu -----------------
    yield True

    # ----------------- Proba amaitu, datuak garbitu -----------------
    # 1. PokemonTaldean ezabatu
    for harrapatu in inserted_harrapatuIds:
        conn.delete(
            "DELETE FROM PokemonTaldean WHERE taldeIzena = ? AND harrapatuId = ? AND erabiltzaileIzena = ?",
            (taldeIzena, harrapatu, erabiltzaileIzena)
        )
    # 2. PokemonTalde ezabatu
    conn.delete(
        "DELETE FROM PokemonTalde WHERE ErabiltzaileIzena = ?",
        (erabiltzaileIzena,)
    )
    # 3. Taldea ezabatu
    conn.delete(
        "DELETE FROM Taldea WHERE taldeIzena = ? AND erabiltzaileIzena = ?",
        (taldeIzena, erabiltzaileIzena)
    )
