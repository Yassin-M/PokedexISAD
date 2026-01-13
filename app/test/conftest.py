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