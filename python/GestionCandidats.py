import mysql.connector

class Candidat:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="bfem"
        )
        self.cur = self.conn.cursor()

    def ajouter_candidat(self, numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, choix_epr, epreuve_facultative, aptitude):
        """Ajoute un candidat dans la base MySQL."""
        query = '''
            INSERT INTO candidat (numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, choix_epr_facultative, epreuve_facultative, aptitude_sportive)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        try:
            self.cur.execute(query, (numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, choix_epr, epreuve_facultative, aptitude))
            self.conn.commit()
            print(f"Candidat {prenom} {nom} ajouté avec succès !")
        except mysql.connector.Error as err:
            print(f"Erreur : {err}")

    def afficher_candidats(self):
        """Récupère tous les candidats de la base de données."""
        self.cur.execute("SELECT * FROM candidat")
        return self.cur.fetchall()

    def supprimer_candidat(self, candidat_id):
        """Supprime un candidat par son ID."""
        self.cur.execute("DELETE FROM candidat WHERE id=%s", (candidat_id,))
        self.conn.commit()

    def fermer_connexion(self):
        """Ferme la connexion MySQL."""
        self.cur.close()
        self.conn.close()
