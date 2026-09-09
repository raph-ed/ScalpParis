import sqlite3
import csv
import io
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from scraper.engine import collecter_donnees_secteur
from scraper.nlp_products import analyser_produits_phares

app = FastAPI(title="Paris Commercial Market Intelligence", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "paris_analytics.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commerces (
            siren TEXT PRIMARY KEY,
            nom TEXT,
            adresse TEXT,
            code_postal TEXT,
            secteur TEXT,
            latitude REAL,
            longitude REAL,
            chiffre_affaires REAL,
            resultat_net REAL,
            marge_nette_pct REAL,
            niveau_affluence TEXT,
            couleur_zone TEXT,
            date_extraction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avis_note INTEGER NOT NULL,
            commentaire TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

class FeedbackPayload(BaseModel):
    avis_note: int = Field(..., ge=1, le=10)
    commentaire: str = Field(..., min_length=2)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/recherche")
async def api_recherche(code_postal: str, secteur: str):
    donnees = await collecter_donnees_secteur(code_postal, secteur)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for row in donnees:
        cur.execute("""
            INSERT OR REPLACE INTO commerces 
            (siren, nom, adresse, code_postal, secteur, latitude, longitude, chiffre_affaires, resultat_net, marge_nette_pct, niveau_affluence, couleur_zone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["siren"], row["nom"], row["adresse"], row["code_postal"], row["secteur"],
            row["latitude"], row["longitude"], row["chiffre_affaires"], row["resultat_net"],
            row["marge_nette_pct"], row["niveau_affluence"], row["couleur_zone"]
        ))
    conn.commit()
    
    # Statistiques directes en SQL
    cur.execute("""
        SELECT 
            AVG(marge_nette_pct), 
            AVG(chiffre_affaires), 
            COUNT(*)
        FROM commerces 
        WHERE code_postal = ? AND secteur = ?
    """, (code_postal, secteur))
    stats = cur.fetchone()
    rendement_moyen = round(stats[0], 2) if stats and stats[0] else 0.0
    ca_moyen = round(stats[1], 2) if stats and stats[1] else 0.0
    nb_commerces = stats[2] if stats else 0
    
    # Top 5 plus rentables
    cur.execute("""
        SELECT nom, adresse, chiffre_affaires, resultat_net, marge_nette_pct 
        FROM commerces 
        WHERE code_postal = ? AND secteur = ?
        ORDER BY marge_nette_pct DESC LIMIT 5
    """, (code_postal, secteur))
    plus_rentables = [
        {"nom": r[0], "adresse": r[1], "ca": r[2], "rn": r[3], "marge": r[4]}
        for r in cur.fetchall()
    ]
    
    # Top 5 moins rentables
    cur.execute("""
        SELECT nom, adresse, chiffre_affaires, resultat_net, marge_nette_pct 
        FROM commerces 
        WHERE code_postal = ? AND secteur = ?
        ORDER BY marge_nette_pct ASC LIMIT 5
    """, (code_postal, secteur))
    moins_rentables = [
        {"nom": r[0], "adresse": r[1], "ca": r[2], "rn": r[3], "marge": r[4]}
        for r in cur.fetchall()
    ]
    conn.close()
    
    produits_phares = analyser_produits_phares(secteur)
    
    # Score d'opportunité d'implantation (sur 100)
    score_opportunite = round(min(100, max(15, (rendement_moyen * 4.2) + (100 / (nb_commerces + 1)))), 1)

    return {
        "statistiques": {
            "rendement_moyen_pct": rendement_moyen,
            "ca_moyen": ca_moyen,
            "nombre_etablissements": nb_commerces,
            "score_opportunite": score_opportunite
        },
        "plus_rentables": plus_rentables,
        "moins_rentables": moins_rentables,
        "produits_phares": produits_phares,
        "etablissements": donnees
    }

@app.post("/api/feedback")
async def api_feedback(payload: FeedbackPayload):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_feedback (avis_note, commentaire) VALUES (?, ?)
    """, (payload.avis_note, payload.commentaire))
    conn.commit()
    conn.close()
    return {"statut": "succes"}

@app.get("/api/feedbacks/liste")
async def api_liste_feedbacks():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT avis_note, commentaire, date_creation FROM user_feedback ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"avis_note": r[0], "commentaire": r[1], "date": r[2]} for r in rows]

@app.get("/api/export")
async def api_export(code_postal: str, secteur: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT siren, nom, adresse, code_postal, secteur, chiffre_affaires, resultat_net, marge_nette_pct, niveau_affluence
        FROM commerces
        WHERE code_postal = ? AND secteur = ?
    """, (code_postal, secteur))
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["SIREN", "NOM", "ADRESSE", "CODE_POSTAL", "SECTEUR", "CHIFFRE_AFFAIRES", "RESULTAT_NET", "MARGE_NETTE_PCT", "AFFLUENCE"])
    for r in rows:
        writer.writerow(r)
        
    output.seek(0)
    filename = f"synthese_marche_{code_postal}_{secteur}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/feedback/csv")
async def api_feedback_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, avis_note, commentaire, date_creation FROM user_feedback ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Avis (Note)", "Commentaire", "Date"])
    for r in rows:
        writer.writerow(r)
        
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=retours_utilisateurs.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
