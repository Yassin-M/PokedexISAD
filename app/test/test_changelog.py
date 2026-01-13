import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def changelog_client(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "test.db"))

    app = create_app()
    app.config["TESTING"] = True

    conn = Connection()

    erabiltzaileak = [
        ("viewer", "pwd", "viewer@example.com", None, "usuario"),
        ("jon", "pwd", "jon@example.com", None, "usuario"),
        ("ane", "pwd", "ane@example.com", None, "usuario"),
        ("june", "pwd", "junez13@example.com", None, "usuario"),
        ("aner", "pwd", "anertxu@example.com", None, "usuario"),
        ("jone", "pwd", "jone2@example.com", None, "usuario"),
    ]
    for erabiltzailea in erabiltzaileak:
        conn.insert(
            "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
            erabiltzailea,
        )

    jarraipenak = [
        ("viewer", "jon", True),
        ("viewer", "ane", True),
        ("viewer", "june", True),
        ("viewer", "aner", True),
    ]
    for jarraitzaileIzena, jarraituIzena, notifikatu in jarraipenak:
        conn.insert(
            "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena, Notifikatu) VALUES (?,?,?)",
            (jarraitzaileIzena, jarraituIzena, notifikatu),
        )

    notifikazioak = [
        ("2025-02-10 10:00:00", "jon", "Jon-ek gimnasio berri bat gainditu du"),
        ("2025-01-15 12:00:00", "june", "June-ek Pikachu harrapatu du"),
        ("2025-01-05 08:30:00", "ane", "Ane-ek domina berri bat lortu du"),
        ("2025-02-12 14:45:00", "jone", "Jone-ek Bulbasaur harrapatu du"),
        ("2025-02-20 09:15:00", "aner", "Aner-ek gimnasio berri bat gainditu du"),
        ("2025-03-01 11:20:00", "aner", "Aner-ek Charizard harrapatu du"),
    ]
    for data, erabiltzailea, deskribapena in notifikazioak:
        conn.insert(
            "INSERT INTO Notifikatu (DataOrdua, ErabiltzaileIzena, deskripzioa) VALUES (?,?,?)",
            (data, erabiltzailea, deskribapena),
        )

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user"] = "viewer"
            session["role"] = "usuario"
        yield client

def test_menu_tiene_boton_changelog(changelog_client):
    respuesta = changelog_client.get("/menu")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    # El menú debe contener el enlace o acción a changelog
    assert "/changelog" in html

def test_click_changelog_redirige_a_changelog(changelog_client):
    respuesta = changelog_client.get("/changelog")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8")

    assert "changelog" in html.lower()

def test_changelog_erantzuna_eta_edukia(changelog_client):
    erantzuna = changelog_client.get("/changelog")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" in edukia
    assert "june" in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia
    assert edukia.count("aner") >= 2


def test_changelog_filtratua_izenez(changelog_client):
    erantzuna = changelog_client.get("/changelog?bilatutako_erabiltzaile_izena=jon")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" in edukia
    assert "june" not in edukia
    assert "aner" not in edukia
    assert "ane" not in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" not in edukia
    assert edukia.count("jon") >= 2

def test_changelog_filtratua_izen_partzialez(changelog_client):
    erantzuna = changelog_client.get("/changelog?bilatutako_erabiltzaile_izena=an")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia

def test_changelog_filtratua_existitzen_ez_den_izenez(changelog_client):
    erantzuna = changelog_client.get("/changelog?bilatutako_erabiltzaile_izena=agapito")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" not in edukia
    assert "ane" not in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" not in edukia
    assert "domina berri" not in edukia


def test_changelog_filtratua_existitzen_diren_izenezkin(changelog_client):
    erantzuna = changelog_client.get("/changelog?bilatutako_erabiltzaile_izena=ane")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia


def test_changelog_tiene_boton_home(changelog_client):
    respuesta = changelog_client.get("/changelog")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    # El botón/enlace Home debe llevar al menú principal
    assert "/menu" in html

def test_home_lleva_al_menu_principal(changelog_client):
    respuesta = changelog_client.get("/menu")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    assert "menu" in html or "principal" in html

