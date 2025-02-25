from turtle import pd

import mysql.connector
import random


class Deliberation:
    def __init__(self):
        """Connexion à la base MySQL."""
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="bfem"
        )
        self.cur = self.conn.cursor()

    def calculer_resultats(self):
        """Calcule les résultats et met à jour les statuts des candidats."""

        # Récupérer les notes des candidats
        self.cur.execute("SELECT * FROM notes")
        notes = self.cur.fetchall()

        for note in notes:
            numero_table = note[0]  # L'ID du candidat
            EPS, CF, ORT = note[1], note[2], note[3]
            TSQ, SVT, ANG1 = note[4], note[5], note[6]
            MATH, HG, IC = note[7], note[8], note[9]
            PC_LV2, ANG2, Ep_FAC = note[10], note[11], note[12]

            # Appliquer les coefficients
            total_points = (
                    CF * 2 + ORT * 1 + TSQ * 1 +
                    HG * 2 + MATH * 4 + PC_LV2 * 2 +
                    SVT * 2 + ANG1 * 2 + ANG2 * 1 + EPS
            )

            # RM2 : Bonus / Malus EPS
            if EPS > 10:
                total_points += EPS - 10
            elif EPS < 10:
                total_points -= (10 - EPS)

            # RM3 : Bonus pour épreuve facultative
            if Ep_FAC > 10:
                total_points += Ep_FAC - 10

            # RM4 à RM6 : Vérifier le passage
            if total_points >= 180:
                statut = "Admis"
            elif total_points >= 153:
                statut = "2nd Tour"
            else:
                statut = "Échec"

            # RM7 : Vérifier repêchage avec moyenne cycle
            self.cur.execute("SELECT moyenne_cycle FROM livret_scolaire WHERE candidat_id=%s", (numero_table,))
            moyenne_cycle = self.cur.fetchone()[0]

            if moyenne_cycle >= 12:
                statut = "Repêchable"

            # RM8 & RM9 : Vérifier repêchage au premier ou au second tour
            if 171 <= total_points <= 179.9:
                statut = "Repêchable - Premier Tour"
            elif 144 <= total_points <= 152.9:
                statut = "Repêchable - Second Tour"

            # RM12 : Vérifier le nombre de tentatives (pas de repêchage après 2 essais)
            self.cur.execute("SELECT nombre_de_fois FROM livret_scolaire WHERE candidat_id=%s", (numero_table,))
            tentatives = self.cur.fetchone()[0]

            if tentatives > 2:
                statut = "Échec Définitif"

            # Mettre à jour le statut du candidat
            self.cur.execute("UPDATE candidat SET statut=%s WHERE id=%s", (statut, numero_table))

        # Sauvegarde
        self.conn.commit()
        print("Délibération terminée !")

    def importer_donnees_excel(self, fichier_excel):
        """Importe les données depuis un fichier Excel et les insère dans la table notes."""
        # Lire le fichier Excel
        df = pd.read_excel(fichier_excel)

        for index, row in df.iterrows():
            candidat_id = row['candidat_id']
            compo_franc = row['compo_franc']
            dictee = row['dictee']
            etude_texte = row['etude_texte']
            histoire_geo = row['histoire_geo']
            mathematiques = row['mathematiques']
            pc_lv2 = row['pc_lv2']
            svt = row['svt']
            anglais1 = row['anglais1']
            anglais_oral = row['anglais_oral']
            eps = row['eps']
            epreuve_facultative = row['epreuve_facultative']

            # Insérer les données dans la table notes
            self.cur.execute("""
                INSERT INTO notes (candidat_id, compo_franc, dictee, etude_texte, 
                histoire_geo, mathematiques, pc_lv2, svt, anglais1, anglais_oral, 
                eps, epreuve_facultative)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (candidat_id, compo_franc, dictee, etude_texte, histoire_geo,
                  mathematiques, pc_lv2, svt, anglais1, anglais_oral, eps, epreuve_facultative))

        # Sauvegarder les changements
        self.conn.commit()
        print("Données importées avec succès depuis le fichier Excel !")


    def generer_anonymat(self):
        """RM13 & RM16 : Génère un numéro d’anonymat unique pour chaque candidat."""
        self.cur.execute("SELECT id FROM candidat")
        candidats = self.cur.fetchall()

        for candidat in candidats:
            candidat_id = candidat[0]
            num_anonymat = random.randint(10000, 99999)

            # Vérifier l'unicité du numéro
            self.cur.execute("SELECT * FROM notes WHERE num_anonymat=%s", (num_anonymat,))
            while self.cur.fetchone():
                num_anonymat = random.randint(10000, 99999)

            # Assigner le numéro au candidat
            self.cur.execute("UPDATE notes SET num_anonymat=%s WHERE candidat_id=%s", (num_anonymat, candidat_id))

        self.conn.commit()
        print("Numéros d'anonymat générés avec succès !")

    def fermer_connexion(self):
        """Ferme la connexion MySQL."""
        self.cur.close()
        self.conn.close()

#Deliberation.importer_donnees_excel('A:/UIDT/Semestre5/POO/Examen/BD_BFEM.xlsx')