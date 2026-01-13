import pytest
from config import Config
from app import create_app
from app.database.database import Connection

@pytest.fixture
def client(tmp_path, monkeypatch):
    # DB temporal
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "test.db"))
    app = create_app()
    app.config["TESTING"] = True

    # Semilla mínima
    conn = Connection()
    conn.insert("INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?, ?, ?, ?, ?)",
                ("ash", "123", "ash@kanto.com", None, "usuario"))
    conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", ("Talde 1", "ash"))

    with app.test_client() as client:
        yield client

def test_taldeak_lista(client):
    with client.session_transaction() as sess:
        sess["user"] = "ash"
        sess["role"] = "usuario"
    resp = client.get("/taldeak")
    assert resp.status_code == 200
    assert b"Talde 1" in resp.data  # Comprueba que se muestra el equipo del usuario

def test_sortu_taldea_redirect(client):
    with client.session_transaction() as sess:
        sess["user"] = "ash"
        sess["role"] = "usuario"
    resp = client.post("/taldea_berria", follow_redirects=False)
    assert resp.status_code == 302  # redirige a la vista del nuevo equipo

class FakeAPI:
    def hartu_stats(self, _): return {"hp": 40, "attack": 50, "special-attack": 60,
                                     "defense": 30, "special-defense": 35, "speed": 70}
    def pokemon_izena_lortu(self, _): return "Pikachu"

def test_sartu_taldera(client, monkeypatch):
    # Parchea API antes de crear el servicio
    monkeypatch.setattr("app.controller.model.eredu_kontroladorea.APIKontroladorea", lambda: FakeAPI())

    # Inserta pokedex + mugimenduak minimoak
    conn = Connection()
    conn.insert("INSERT INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa, irudia, generazioa, preEboluzioId) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (25, "Pikachu", 0.4, 6, "M/F", "desc", "/img", 1, None))
    conn.insert("INSERT INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) "
                "VALUES (?,?,?,?,?,?)", ("Impactrueno", 40, 100, 30, "", "Electric"))
    conn.insert("INSERT INTO IkasDezake (pokedexId, mugiIzena) VALUES (?,?)", (25, "Impactrueno"))
    with client.session_transaction() as sess:
        sess["user"] = "ash"
        sess["role"] = "usuario"
        sess["editatzen_ari_den_taldea"] = "Talde 1"
        sess["pokemon_datuak"] = 25

    resp = client.post("/pokemon_taldea", follow_redirects=False)
    assert resp.status_code == 302  # redirige de vuelta a taldea
    # Comprueba que se guardó la relación
    rows = conn.select("SELECT COUNT(*) AS n FROM PokemonTaldean WHERE taldeIzena=? AND erabiltzaileIzena=?", ("Talde 1", "ash"))
    assert rows[0]["n"] == 1