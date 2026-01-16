import pytest

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def admin_client(tmp_path, monkeypatch):
    """Admin probetarako app eta DB isolatua sortu."""
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "admin_test.db"))
    app = create_app()
    app.config["TESTING"] = True

    conn = Connection()
    erabiltzaileak = [
        ("Jon", "Jon123", "jon@adibidea.com", None, "admin"),
        ("Ane", "Ane123", "ane@adibidea.com", None, "usuario"),
        ("Mikel", "Mikel123", "mikel@adibidea.com", None, "usuario"),
        ("Iker", "Iker123", "iker@adibidea.com", None, "usuario"),
    ]
    for row in erabiltzaileak:
        conn.insert(
            "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
            row,
        )

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "Jon"
        sess["role"] = "admin"

    return client


# 3.1.23: Menu admin eta KUDEATU orrira sartzen da
def test_kudeatu_menu_admin(admin_client):
    erantzuna = admin_client.get("/kudeatu")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "KUDEATU ERABILTZAILEAK" in html
    assert "Ane" in html
    assert "Mikel" in html


# 3.1.24: EDITATU botoia eta editazio orrira sartzen da
def test_editatu_usuario(admin_client):
    erantzuna = admin_client.get("/kudeatu/editatu/Ane")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Profila Editatu" in html
    assert "izena" in html
    assert "email" in html


# 3.1.25: Eremu hutsik uzten du eta GORDE
def test_eremu_hutsik_gorde(admin_client):
    erantzuna = admin_client.post(
        "/kudeatu/editatu/Ane",
        data={
            "izena": "",
            "email": "ane@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "",
            "pasahitza2": "",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu/editatu/Ane"
    assert "Mesedez, bete eremu guztiak" in html


# 3.1.26: Pasahitza karaktere bereziak ditu
def test_pasahitza_karaktere_bereziak(admin_client):
    erantzuna = admin_client.post(
        "/kudeatu/editatu/Ane",
        data={
            "izena": "Ane",
            "email": "ane@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "Pass|123",
            "pasahitza2": "Pass|123",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu/editatu/Ane"
    assert "Pasahitzak ezin du karaktere hau izan:" in html


# 3.1.27: Pasahitzak ez datoz bat
def test_pasahitzak_ezberdinak(admin_client):
    erantzuna = admin_client.post(
        "/kudeatu/editatu/Ane",
        data={
            "izena": "Ane",
            "email": "ane@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "Pass123",
            "pasahitza2": "Pass456",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu/editatu/Ane"
    assert "Pasahitzak ez datoz bat" in html


# 3.1.28: Datuak behar bezala eguneratzen dira
def test_datuak_eguneratzen_dira(admin_client):
    erantzuna = admin_client.post(
        "/kudeatu/editatu/Ane",
        data={
            "izena": "Ane",
            "email": "ane_berria@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "AnePass123",
            "pasahitza2": "AnePass123",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu/editatu/Ane"
    assert "Datuak behar bezala eguneratu dira" in html


# 3.1.29: Izen hartatua dagoen arazoa
def test_izen_hartatua_dagoen(admin_client):
    erantzuna = admin_client.post(
        "/kudeatu/editatu/Mikel",
        data={
            "izena": "Ane",
            "email": "mikel@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "",
            "pasahitza2": "",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu/editatu/Mikel"
    assert "Izen hori hartuta dago" in html


# 3.1.30: HOME botoiak menu admin-era bueltatzen du
def test_home_botoia_menu_admin(admin_client):
    erantzuna = admin_client.get("/menu_admin")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/menu_admin"


# 3.1.31: Erabiltzaile bat ezabatzen du
def test_ezabatu_usuario(admin_client):
    erantzuna = admin_client.get(
        "/kudeatu/ezabatu/Mikel",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu"
    assert "Mikel" not in html


# 3.1.32: Bilatzaile eremu hutsik
def test_bilatzaile_hutsik(admin_client):
    erantzuna = admin_client.get("/kudeatu")

    erantzuna_filter = admin_client.post(
        "/kudeatu",
        data={"bilaketa": ""},
        follow_redirects=True,
    )

    html = erantzuna_filter.data.decode("utf-8")

    assert erantzuna_filter.status_code == 200


# 3.1.33: Bilatzaile existitzen ez den erabiltzailea
def test_bilatzaile_ez_dago(admin_client):
    erantzuna = admin_client.get("/kudeatu")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "KUDEATU ERABILTZAILEAK" in html


# 3.1.34: Bilatzaile existitzen den erabiltzailea
def test_bilatzaile_existitzen_dago(admin_client):
    erantzuna = admin_client.get("/kudeatu")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Ane" in html or "Iker" in html


# 3.1.35: Erabiltzaile bat admin bihurtzen du
def test_admin_bihurtu(admin_client):
    erantzuna = admin_client.get(
        "/kudeatu/admin/Iker",
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/kudeatu"
    assert "Iker" in html


# 3.1.36: HOME botoiak menu admin-era bueltatzen du berriro
def test_home_botoia_menu_admin_berriro(admin_client):
    erantzuna = admin_client.get("/menu_admin")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/menu_admin"
