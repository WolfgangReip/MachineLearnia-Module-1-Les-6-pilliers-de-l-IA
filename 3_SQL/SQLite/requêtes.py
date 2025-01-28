import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('bibliotheque.db')

# Enable foreign keys
conn.execute("PRAGMA foreign_keys = ON;")


def fetch_and_display(query, conn):
    try:
        df = pd.read_sql_query(query, conn)
        print(df)  
        return df  
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


# 3. Afficher les livres disponibles
try:
    print("📚 Livres disponibles :")
    fetch_and_display('SELECT Titre FROM Livres WHERE Disponible = 1', conn)
except Exception as e:
    print(f"Error in query 'Livres disponibles': {e}")

# 4. Trier les livres par Date de Publication
try:
    print("\n📅 Livres triés par date de publication :")
    fetch_and_display("SELECT * FROM Livres ORDER BY DatePublication DESC", conn)
except Exception as e:
    print(f"Error in query 'Livres triés par date de publication': {e}")

# 5. Filtrer les Emprunts en Cours
try:
    print("\n📌 Emprunts en cours :")
    fetch_and_display("SELECT * FROM Emprunts WHERE DateRetourEffective IS NULL", conn)
except Exception as e:
    print(f"Error in query 'Emprunts en cours': {e}")

# 6. Calculer la Durée d'un Emprunt
try:
    print("\n⏳ Durée des emprunts (en jours) :")
    fetch_and_display("""
        SELECT EmpruntID, DateEmprunt, DateRetourPrévue, DateRetourEffective, 
        julianday(REPLACE(DateRetourEffective, '−', '-')) - julianday(REPLACE(DateEmprunt, '−', '-')) AS DureeEmprunt
        FROM Emprunts 
        WHERE DateRetourEffective IS NOT NULL;
    """, conn)
except Exception as e:
    print(f"Error in query 'Durée des emprunts': {e}")

# 7. Jointure sur les Livres et les Auteurs
try:
    print("\n📚 Jointure sur les Livres et les Auteurs :")
    fetch_and_display("SELECT Livres.Titre FROM Livres LEFT JOIN Auteurs on Livres.AuteurID = Auteurs.AuteurID", conn)
except Exception as e:
    print(f"Error in query 'Jointure sur les Livres et les Auteurs': {e}")

# 8. Filtrer les Emprunteurs qui n’ont pas encore rendu de livres
try:
    print("\n📌 Emprunteurs qui n'ont pas encore rendu de livres :")
    fetch_and_display("""
        SELECT DISTINCT Emprunteurs.EmprunteurID, Emprunteurs.Nom, Emprunteurs.Prénom, Emprunteurs.Email 
        FROM Emprunteurs 
        LEFT JOIN Emprunts ON Emprunteurs.EmprunteurID = Emprunts.EmprunteurID 
        GROUP BY Emprunteurs.EmprunteurID
        HAVING SUM(CASE WHEN Emprunts.DateRetourEffective IS NULL THEN 1 ELSE 0 END) > 0;
    """, conn)
except Exception as e:
    print(f"Error in query 'Emprunteurs qui n'ont pas encore rendu de livres': {e}")

# 9. Nombre de Livres par Genre
try:
    print("\n📚 Nombre de livres par genre :")
    fetch_and_display("""
        SELECT Genres.NomGenre, COUNT(Livres.LivreID) as NombreLivres
        FROM Genres
        LEFT JOIN Livres ON Genres.GenreID = Livres.GenreID
        GROUP BY Genres.GenreID;
    """, conn)
except Exception as e:
    print(f"Error in query 'Nombre de livres par genre': {e}")

# 10. Durée Moyenne d’Emprunt par Emprunteur
try:
    print("\n⏳ Durée moyenne d'emprunt par emprunteur (en jours) :")
    fetch_and_display("""
        SELECT 
            Emprunteurs.Nom, 
            Emprunteurs.Prénom, 
            AVG(julianday(REPLACE(Emprunts.DateRetourEffective, '−', '-')) - 
                julianday(REPLACE(Emprunts.DateEmprunt, '−', '-'))) AS DuréeMoyenne
        FROM 
            Emprunteurs
        INNER JOIN 
            Emprunts 
        ON 
            Emprunteurs.EmprunteurID = Emprunts.EmprunteurID
        WHERE 
            Emprunts.DateRetourEffective IS NOT NULL
        GROUP BY 
            Emprunteurs.Nom, Emprunteurs.Prénom;
    """, conn)
except Exception as e:
    print(f"Error in query 'Durée moyenne d'emprunt par emprunteur': {e}")

# 11. Jointure avec Emprunteurs, Livres, et Genres
try:
    print("\n📚 Jointure avec Emprunteurs, Livres, et Genres :")
    fetch_and_display("""
        SELECT Livres.Titre, Emprunteurs.Nom, Genres.NomGenre
        FROM Livres
        LEFT JOIN Emprunts ON Livres.LivreID = Emprunts.LivreID
        LEFT JOIN Emprunteurs ON Emprunts.EmprunteurID = Emprunteurs.EmprunteurID
        LEFT JOIN Genres ON Livres.GenreID = Genres.GenreID
        
        UNION
        
        SELECT Livres.Titre, Emprunteurs.Nom, Genres.NomGenre
        FROM Emprunteurs
        LEFT JOIN Emprunts ON Emprunteurs.EmprunteurID = Emprunts.EmprunteurID
        LEFT JOIN Livres ON Emprunts.LivreID = Livres.LivreID
        LEFT JOIN Genres ON Livres.GenreID = Genres.GenreID;
    """, conn)
except Exception as e:
    print(f"Error in query 'Jointure avec Emprunteurs, Livres, et Genres': {e}")

# 12. Livres les Plus Empruntés
try:
    print("\n📚 Livres les plus empruntés :")
    fetch_and_display("""
        SELECT Livres.Titre, COUNT(Emprunts.LivreID) as NombreEmprunts
        FROM Livres
        LEFT JOIN Emprunts ON Livres.LivreID = Emprunts.LivreID
        GROUP BY Livres.LivreID
        ORDER BY NombreEmprunts DESC;
    """, conn)
except Exception as e:
    print(f"Error in query 'Livres les plus empruntés': {e}")

# 13. Nombre de Livres Empruntés par Emprunteur
try:
    print("\n📚 Nombre de livres empruntés par emprunteur :")
    fetch_and_display("""
        SELECT Emprunteurs.Nom, Emprunteurs.Prénom, COUNT(Emprunts.LivreID) as NombreLivresEmpruntés
        FROM Emprunteurs
        LEFT JOIN Emprunts ON Emprunteurs.EmprunteurID = Emprunts.EmprunteurID
        GROUP BY Emprunteurs.EmprunteurID
        ORDER BY NombreLivresEmpruntés DESC;
    """, conn)
except Exception as e:
    print(f"Error in query 'Nombre de livres empruntés par emprunteur': {e}")

# 14. Livres Jamais Empruntés
try:
    print("\n📚 Livres jamais empruntés :")
    fetch_and_display("""
        SELECT Livres.Titre
        FROM Livres
        LEFT JOIN Emprunts ON Livres.LivreID = Emprunts.LivreID
        WHERE Emprunts.LivreID IS NULL;
    """, conn)
except Exception as e:
    print(f"Error in query 'Livres jamais empruntés': {e}")

# 15. Nombre d’Emprunteurs par Auteur
try:
    print("\n📌 Nombre d'emprunteurs par auteur :")
    fetch_and_display("""
        SELECT Auteurs.Nom, Auteurs.Prénom, COUNT(Emprunts.EmprunteurID) as NombreEmprunteurs
        FROM Auteurs
        LEFT JOIN Livres ON Auteurs.AuteurID = Livres.AuteurID
        LEFT JOIN Emprunts ON Livres.LivreID = Emprunts.LivreID
        GROUP BY Auteurs.AuteurID
        ORDER BY NombreEmprunteurs DESC;
    """, conn)
except Exception as e:
    print(f"Error in query 'Nombre d'emprunteurs par auteur': {e}")

# Close the connection
conn.close()
