import pytest

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def lagunak_client(tmp_path, monkeypatch):
    """Lagunak probetarako app eta DB isolatua sortu."""
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "lagunak_test.db"))
    app = create_app()
    app.config["TESTING"] = True

    conn = Connection()
    erabiltzaileak = [
        ("Jon", "Jon123", "jon@adibidea.com", None, "usuario"),
        ("Ane", "Ane123", "ane@adibidea.com", None, "usuario"),
        ("Mikel", "Mikel123", "mikel@adibidea.com", None, "usuario"),
        ("Iker", "Iker123", "iker@adibidea.com", None, "usuario"),
    ]
    for row in erabiltzaileak:
        conn.insert(
            "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
            row,
        )

    # Jon jada Ane jarraitzen du (notifikazioak aktibo), Mikel isilarazita dago
    conn.insert(
        "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena, Notifikatu) VALUES (?,?,?)",
        ("Jon", "Ane", True),
    )
    conn.insert(
        "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena, Notifikatu) VALUES (?,?,?)",
        ("Jon", "Mikel", False),
    )

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "Jon"
        sess["role"] = "usuario"

    return client


# 3.1.12: Menuan LAGUNAK orrira sartzen da
def test_lagunak_orrian_agertzen_da(lagunak_client):
    erantzuna = lagunak_client.get("/lagunak")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "LAGUNAK" in html
    assert "GEHITU" in html


# 3.1.13: GEHITU botoia eta bilatzaile orria
def test_gehitu_botoia_bilatzaileara(lagunak_client):
    erantzuna = lagunak_client.get("/gehituErabiltzailea")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "ERABILTZAILEAK BILATU" in html
    assert "Hasi bilaketa erabiltzaileak aurkitzeko" in html


# 3.1.14: Bilaketa hutsik egiten du
def test_bilaketa_hutsik(lagunak_client):
    erantzuna = lagunak_client.get("/gehituErabiltzailea?bilaketa=")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Hasi bilaketa erabiltzaileak aurkitzeko" in html


# 3.1.15: Ez dagoen erabiltzailea bilatzen du
def test_bilaketa_ez_dago(lagunak_client):
    erantzuna = lagunak_client.get("/gehituErabiltzailea?bilaketa=EzDago")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Ez da erabiltzailerik aurkitu" in html


# 3.1.16: Dagoen lagun bat bilatzen du
def test_bilaketa_lagun_jarraitua(lagunak_client):
    erantzuna = lagunak_client.get("/gehituErabiltzailea?bilaketa=Ane")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Jarraitzen" in html


# 3.1.17: Jarraitzen ez duen lagun bat gehitzen du
def test_jarraitu_lagun_berria(lagunak_client):
    erantzuna = lagunak_client.get(
        "/gehituErabiltzailea/Iker?bilaketa=Iker",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/gehituErabiltzailea"
    assert "Orain jarraitzen duzu erabiltzaile hau" in html


# 3.1.18: HOME botoia menura bueltatzen da
def test_home_botoia_menura(lagunak_client):
    erantzuna = lagunak_client.get("/menu")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/menu"
    assert "TALDEAK" in erantzuna.data.decode("utf-8")


# 3.1.19: UTZI JARRAITZEN botoia

def test_utzi_jarraitzen(lagunak_client):
    erantzuna = lagunak_client.get(
        "/lagunak/utzi/Ane",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/lagunak"
    assert "Jarraitzea eten da" in html
    assert "Ane" not in html


# 3.1.20: Notifikazioak isilarazi (aktibo zegoena)

def test_notifikazioak_isilarazi(lagunak_client):
    erantzuna = lagunak_client.get(
        "/lagunak/notifikazioak/Ane?isilarazi=false",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/lagunak"
    assert "Notifikazioak eguneratuta daude" in html
    assert "🔕" in html


# 3.1.21: Notifikazioak aktibatu (isilarazita zegoena)

def test_notifikazioak_aktibatu(lagunak_client):
    erantzuna = lagunak_client.get(
        "/lagunak/notifikazioak/Mikel?isilarazi=true",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/lagunak"
    assert "Notifikazioak eguneratuta daude" in html
    assert "🔔" in html


# 3.1.22: HOME botoia berriro menura

def test_home_botoia_menura_notifikazioak(lagunak_client):
    erantzuna = lagunak_client.get("/menu")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/menu"
    assert "TALDEAK" in erantzuna.data.decode("utf-8")
