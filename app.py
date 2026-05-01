from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS voyages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agence TEXT,
        depart TEXT,
        destination TEXT,
        tarif INTEGER,
        temps REAL
    )
    """)
    conn.commit()

@app.route("/")
def index():
    conn = get_db()
    voyages = conn.execute("SELECT * FROM voyages ORDER BY id DESC").fetchall()
    return render_template("index.html", voyages=voyages)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        agence = request.form["agence"]
        depart = request.form["depart"]
        destination = request.form["destination"]
        tarif = request.form["tarif"]
        temps = request.form["temps"]

        conn = get_db()
        conn.execute(
            "INSERT INTO voyages (agence, depart, destination, tarif, temps) VALUES (?, ?, ?, ?, ?)",
            (agence, depart, destination, tarif, temps)
        )
        conn.commit()

        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM voyages WHERE id = ?", (id,))
    conn.commit()
    return redirect(url_for("index"))

@app.route("/stats")
def stats():
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM voyages").fetchone()[0]
    avg_price = conn.execute("SELECT AVG(tarif) FROM voyages").fetchone()[0]
    avg_time = conn.execute("SELECT AVG(temps) FROM voyages").fetchone()[0]

    agences = conn.execute("""
        SELECT agence, COUNT(*) as total, AVG(tarif) as avg_price
        FROM voyages
        GROUP BY agence
    """).fetchall()

    trajets = conn.execute("""
        SELECT depart, destination, COUNT(*) as total
        FROM voyages
        GROUP BY depart, destination
    """).fetchall()

    # 🔥 Données pour graphiques
    agences_labels = [a["agence"] for a in agences]
    agences_prices = [a["avg_price"] for a in agences]

    trajets_labels = [f"{t['depart']} → {t['destination']}" for t in trajets]
    trajets_counts = [t["total"] for t in trajets]

    return render_template("stats.html",
                           total=total,
                           avg_price=avg_price,
                           avg_time=avg_time,
                           agences=agences,
                           trajets=trajets,
                           agences_labels=json.dumps(agences_labels),
                           agences_prices=json.dumps(agences_prices),
                           trajets_labels=json.dumps(trajets_labels),
                           trajets_counts=json.dumps(trajets_counts))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)