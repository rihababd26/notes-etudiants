import json
import pytest
import app as application
import auth

from app import app

client = app.test_client()

JETONS = {
    "jeton-prof-devsecops": {
        "nom": "Pr. Alami",
        "role": "enseignant",
        "module": "DevSecOps"
    },
    "jeton-prof-java": {
        "nom": "Pr. Bennani",
        "role": "enseignant",
        "module": "Java"
    },
    "jeton-amina": {
        "nom": "Amina",
        "role": "etudiant",
        "module": None
    }
}


@pytest.fixture(autouse=True)
def environnement_test(tmp_path, monkeypatch):
    fichier_jetons = tmp_path / "jetons.json"
    fichier_jetons.write_text(
        json.dumps(JETONS),
        encoding="utf-8"
    )

    monkeypatch.setattr(auth, "FICHIER_JETONS", str(fichier_jetons))

    base_test = tmp_path / "notes.db"
    monkeypatch.setattr(application, "DB", str(base_test))

    application.init_db()


def modifier(note, jeton=None):
    headers = {}

    if jeton:
        headers["Authorization"] = f"Bearer {jeton}"

    return client.put(
        "/notes/1",
        json={"note": note},
        headers=headers
    )


# S1 : protection contre les injections SQL
def test_injection_sql():
    response = client.get("/notes?etudiant=' OR '1'='1")
    assert response.status_code == 200
    assert response.json == []


# S2 : authentification obligatoire
def test_sans_authentification():
    response = modifier(17)
    assert response.status_code == 401


# S3 : un étudiant ne peut pas modifier une note
def test_etudiant_interdit():
    response = modifier(17, "jeton-amina")
    assert response.status_code == 403


# S4 : un enseignant ne peut modifier que les notes de son module
def test_mauvais_module():
    response = modifier(17, "jeton-prof-java")
    assert response.status_code == 403


# S5 : validation de la note
@pytest.mark.parametrize("note", [25, "20 WHERE 1=1"])
def test_note_invalide(note):
    response = modifier(note, "jeton-prof-devsecops")
    assert response.status_code == 400


# S6 : modification autorisée
def test_modification_autorisee():
    response = modifier(17, "jeton-prof-devsecops")
    assert response.status_code == 200

    response = client.get("/notes?etudiant=Amina")
    assert response.json[0]["note"] == 17


# S7 : ne pas révéler les détails techniques
def test_erreur_sans_details_techniques(monkeypatch):
    def erreur_db(*args, **kwargs):
        raise Exception("database password secret")

    monkeypatch.setattr(application.sqlite3, "connect", erreur_db)

    response = modifier(17, "jeton-prof-devsecops")

    assert response.status_code == 500
    assert "database" not in response.get_data(as_text=True).lower()