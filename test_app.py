
import app as notes_app

# Initialiser la base de données pour les tests
notes_app.init_db()

client = notes_app.app.test_client()


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "API des notes des etudiants"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_get_all_notes():
    response = client.get("/notes")
    assert response.status_code == 200
    assert len(response.json) == 2


def test_filter_notes_by_etudiant():
    response = client.get("/notes?etudiant=Amina")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["etudiant"] == "Amina"
    assert response.json[0]["note"] == 15.5
