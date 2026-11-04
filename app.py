
from flask import Flask, request
import sqlite3
from auth import utilisateur_connecte


app = Flask(__name__)
DB = "notes.db"
DATABASE = DB


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etudiant TEXT NOT NULL,
                matiere TEXT NOT NULL,
                note REAL NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM notes"
        ).fetchone()[0]

        if count == 0:
            conn.executemany(
                "INSERT INTO notes (etudiant, matiere, note) VALUES (?, ?, ?)",
                [
                    ("Amina", "DevSecOps", 15.5),
                    ("Youssef", "DevSecOps", 12.0),
                ],
            )

#page d'acceil(home)
@app.route("/")
def home():
    return {"message": "API des notes des etudiants"}


@app.route("/health")
def health():
    return {"status": "ok", "version": "1.0"}


@app.route("/notes")
def get_notes():
    etudiant = request.args.get("etudiant")

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row

        if etudiant:
            rows = conn.execute(
                "SELECT etudiant, matiere, note FROM notes WHERE etudiant = ?",
                (etudiant,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT etudiant, matiere, note FROM notes"
            ).fetchall()

    return [dict(row) for row in rows]

# Modification d'une note par l'enseignant

# Modification sécurisée d'une note par l'enseignant
@app.route("/notes/<int:note_id>", methods=["PUT"])
def modifier_note(note_id):
    utilisateur = utilisateur_connecte()

    # Vérifier l'authentification
    if utilisateur is None:
        return {"erreur": "Authentification requise"}, 401

    # Vérifier le rôle
    if utilisateur.get("role") != "enseignant":
        return {"erreur": "Accès interdit"}, 403

    try:
        donnees = request.get_json()
        nouvelle_note = donnees.get("note")

        # Vérifier la note
        if isinstance(nouvelle_note, bool):
            return {"erreur": "Note invalide"}, 400

        nouvelle_note = float(nouvelle_note)

        if not 0 <= nouvelle_note <= 20:
            return {"erreur": "Note invalide"}, 400

        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row

            ligne = conn.execute(
                "SELECT matiere FROM notes WHERE id = ?",
                (note_id,)
            ).fetchone()

            if ligne is None:
                return {"erreur": "Note introuvable"}, 404

            # Vérifier le module de l'enseignant
            if utilisateur.get("module") != ligne["matiere"]:
                return {"erreur": "Accès interdit"}, 403

            conn.execute(
                "UPDATE notes SET note = ? WHERE id = ?",
                (nouvelle_note, note_id)
            )

        return {"message": "Note modifiée avec succès"}, 200

    except (ValueError, TypeError, AttributeError):
        return {"erreur": "Note invalide"}, 400

    except Exception:
        return {"erreur": "Une erreur interne est survenue"}, 500


if __name__ == "__main__":
    init_db()
    app.run(debug=False)
