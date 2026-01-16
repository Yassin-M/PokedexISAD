import pytest

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def editatu_client(tmp_path, monkeypatch):
    """Editatu probetarako app eta DB isolatua sortu."""
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "editatu_test.db"))
    app = create_app()
    app.config["TESTING"] = True

    conn = Connection()
    erabiltzaileak = [
        ("Jon", "Jon123", "jon@adibidea.com", None, "usuario"),
        ("Ane", "Ane123", "ane@adibidea.com", None, "usuario"),
        ("Mikel", "Mikel123", "mikel@adibidea.com", None, "usuario"),
    ]
    for row in erabiltzaileak:
        conn.insert(
            "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
            row,
        )

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "Jon"
        sess["role"] = "usuario"

    return client


# 3.1.37: EDITATU botoia eta profila editatzeko orrira sartzen da
def test_editatu_botoia_orrira(editatu_client):
    erantzuna = editatu_client.get("/editatu")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert "Profila Editatu" in html
    assert "izena" in html
    assert "email" in html


# 3.1.38: Eremu hutsik uzten du eta GORDE
def test_eremu_hutsik_gorde(editatu_client):
    erantzuna = editatu_client.post(
        "/editatu",
        data={
            "izena": "",
            "email": "jon@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "",
            "pasahitza2": "",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/editatu"
    assert "Mesedez, bete eremu guztiak" in html


# 3.1.39: Pasahitza karaktere bereziak ditu
def test_pasahitza_karaktere_bereziak(editatu_client):
    erantzuna = editatu_client.post(
        "/editatu",
        data={
            "izena": "Jon",
            "email": "jon@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "Pass|123",
            "pasahitza2": "Pass|123",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/editatu"
    assert "Pasahitzak ezin du karaktere hau izan:" in html


# 3.1.40: Pasahitzak ez datoz bat
def test_pasahitzak_ezberdinak(editatu_client):
    erantzuna = editatu_client.post(
        "/editatu",
        data={
            "izena": "Jon",
            "email": "jon@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "Pass123",
            "pasahitza2": "Pass456",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/editatu"
    assert "Pasahitzak ez datoz bat" in html


# 3.1.41: Izen hartatua dagoen arazoa
def test_izen_hartatua_dagoen(editatu_client):
    erantzuna = editatu_client.post(
        "/editatu",
        data={
            "izena": "Ane",
            "email": "jon@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "",
            "pasahitza2": "",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/editatu"
    assert "Izen hori hartuta dago" in html


# 3.1.42: Datuak behar bezala eguneratzen dira
def test_datuak_eguneratzen_dira(editatu_client):
    erantzuna = editatu_client.post(
        "/editatu",
        data={
            "izena": "Jon",
            "email": "jon_berria@adibidea.com",
            "jaiotza": "2000-01-01",
            "pasahitza": "JonPass123",
            "pasahitza2": "JonPass123",
        },
        follow_redirects=True,
    )

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/editatu"
    assert "Datuak behar bezala eguneratu dira" in html


# 3.1.43: HOME botoiak menu nagusira bueltatzen du
def test_home_botoia_menu_nagusia(editatu_client):
    erantzuna = editatu_client.get("/menu")

    html = erantzuna.data.decode("utf-8")

    assert erantzuna.status_code == 200
    assert erantzuna.request.path == "/menu"
    assert "TALDEAK" in html
