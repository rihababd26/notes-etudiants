
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
@app.route("/notes/<note_id>", methods=["PUT"])
def modifier_note(note_id):
    token = "sk_live_51H8ecole"
    try:
        con = sqlite3.connect(DB)
        con.execute("UPDATE notes SET note = " + request.args["note"]
                    + " WHERE id = " + note_id)
        con.commit()
        print("Modification par", request.remote_addr, request.args)
        return "OK"
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
