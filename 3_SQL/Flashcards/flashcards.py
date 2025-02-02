import pandas as pd
import sqlite3
import datetime


def init_db():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    # Créer les tables et insérer les thèmes
    c.execute('''
    CREATE TABLE IF NOT EXISTS Cards(
        id INTEGER PRIMARY KEY,
        question TEXT,
        reponse TEXT,
        probailite REAL,
        id_theme INTEGER, 
        FOREIGN KEY (id_theme) REFERENCES themes(id) ON DELETE RESTRICT
    ); 
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS themes(
            id INTEGER PRIMARY KEY,
            theme TEXT
        );
        ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS stats(
            id INTEGER PRIMARY KEY,
            bonnes_reponses INTEGER,
            mauvaises_reponses INTEGER,
            date DATE
        );
        ''')
    
    conn.commit()
    print("Tables créées avec succès")
    conn.close()
    

def create_card(question, reponse, probabilite, id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("INSERT INTO Cards(question, reponse, probabilite, id_theme) VALUES (?, ?, ?, ?)", (question, reponse, probabilite, id_theme))
    conn.commit()
    conn.close()

def get_card(id):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Cards WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    return row

def update_card(id, question, reponse, probabilite, id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("UPDATE Cards SET question = ?, reponse = ?, probabilite = ?, id_theme = ? WHERE id = ?", (question, reponse, probabilite, id_theme, id))
    conn.commit()
    conn.close()
    
def delete_card(id):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("DELETE FROM Cards WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_all_cards():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Cards")
    rows = c.fetchall()
    conn.close()
    return rows

def get_number_of_cards():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Cards")
    rows = c.fetchone()
    conn.close()
    return rows[0]

def get_cards_by_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Cards WHERE id_theme = ?", (id_theme,))
    rows = c.fetchall()
    conn.close()
    return rows


def create_theme(theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("INSERT INTO themes(theme) VALUES (?)", (theme,))
    conn.commit()
    conn.close()

def get_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM themes WHERE id = ?", (id_theme,))
    row = c.fetchone()
    conn.close()
    return row

def update_theme(id_theme, theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("UPDATE themes SET theme = ? WHERE id = ?", (theme, id_theme))
    conn.commit()
    conn.close()
    
def delete_theme(id_theme):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("DELETE FROM themes WHERE id = ?", (id_theme,))
    conn.commit()
    conn.close()

def get_all_themes():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT * FROM themes")
    rows = c.fetchall()
    conn.close()
    return rows


# Fonctions :
# — update_stats(is_correct) pour mettre à jour la base stats suivant les indications ci-
# dessous
# — update_card_probability(card_id, is_correct) pour mettre à jour la probabilité d’ap-
# parition d’une carte
# — get_stats() pour récupérer les statistiques au travers du temps
# Description : Ces fonctions gèrent les statistiques des réponses des utilisateurs, telles que le
# nombre de bonnes et mauvaises réponses, ainsi que la probabilité d’affichage des cartes.
# — Utilisez SELECT pour récupérer les statistiques existantes.
# — Utilisez UPDATE pour modifier les statistiques en fonction des réponses.
# — Utilisez INSERT INTO pour ajouter de nouvelles entrées de statistiques.
# — Calculez les probabilités en fonction des réponses correctes ou incorrectes.
# — Utilisez la bibliothèque datetime pour gérer les dates.

def update_stats(is_correct):
    """
    Met à jour les statistiques (bonnes/mauvaises réponses) pour la date du jour.
    - is_correct : bool indiquant si la réponse est correcte (True) ou non (False).
    """
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    # Récupère la date du jour au format ISO (YYYY-MM-DD)
    today = datetime.date.today().isoformat()

    # Vérifie s'il existe déjà une entrée pour la date du jour
    c.execute("""
        SELECT id, bonnes_reponses, mauvaises_reponses 
        FROM stats 
        WHERE date = ?
    """, (today,))
    row = c.fetchone()

    if row:
        # On met à jour l'entrée existante
        stat_id, bonnes, mauvaises = row
        if is_correct:
            bonnes += 1
        else:
            mauvaises += 1

        c.execute("""
            UPDATE stats
            SET bonnes_reponses = ?, mauvaises_reponses = ?
            WHERE id = ?
        """, (bonnes, mauvaises, stat_id))
    else:
        # On crée une nouvelle entrée pour la date du jour
        bonnes = 1 if is_correct else 0
        mauvaises = 0 if is_correct else 1

        c.execute("""
            INSERT INTO stats (bonnes_reponses, mauvaises_reponses, date)
            VALUES (?, ?, ?)
        """, (bonnes, mauvaises, today))

    conn.commit()
    conn.close()


def update_card_probability(card_id, is_correct):
    """
    Met à jour la probabilité d'apparition d'une carte en fonction
    du fait que la réponse est correcte ou non.
    - card_id : identifiant de la carte
    - is_correct : bool indiquant si la réponse est correcte (True) ou non (False).
    """
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    # Récupère la probabilité actuelle de la carte
    c.execute("SELECT probabilite FROM Cards WHERE id = ?", (card_id,))
    row = c.fetchone()

    if not row:
        # Si la carte n'existe pas, on sort de la fonction
        conn.close()
        return
    
    current_prob = row[0]

    # Logique d'ajustement de probabilité (exemple avec simple facteur multiplicatif)
    if is_correct:
        # Diminue légèrement la probabilité si la réponse est correcte
        new_prob = current_prob * 0.9
    else:
        # Augmente légèrement la probabilité si la réponse est incorrecte
        new_prob = current_prob * 1.1

    # On borne la probabilité entre 0 et 1
    new_prob = max(0.0, min(new_prob, 1.0))

    # Mise à jour de la probabilité
    c.execute("""
        UPDATE Cards 
        SET probabilite = ?
        WHERE id = ?
    """, (new_prob, card_id))

    conn.commit()
    conn.close()


def get_stats():
    """
    Récupère l'ensemble des statistiques enregistrées, triées par date.
    Retourne une liste de tuples : (id, bonnes_reponses, mauvaises_reponses, date).
    """
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()

    c.execute("""
        SELECT id, bonnes_reponses, mauvaises_reponses, date 
        FROM stats 
        ORDER BY date
    """)
    rows = c.fetchall()

    conn.close()
    return rows