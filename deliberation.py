import sqlite3
import random
from base_de_donnees import BaseDeDonnees


class Deliberation:
    def __init__(self):
        """Initialisation de la base de données via BaseDeDonnees"""
        self.bdd = BaseDeDonnees()
        self.conn = self.bdd.conn
        self.cur = self.bdd.cur

    def calculer_resultats(self):
        """Calcule les résultats et met à jour les statuts des candidats."""
        self.cur.execute(""" 
            SELECT c.numero_table, c.Type_candidat, c.Etat_sportif, c.Nb_F,
                   n.EPS, n.CF, n.ORT, n.TSQ, n.SVT, n.ANG1, n.MATH, n.HG, n.IC, n.PC_LV2, 
                   n.ANG2, n.Ep_FAC, l.moy_6e, l.moy_5e, l.moy_4e, l.moy_3e, l.nombre_de_fois, c.num_anonymat
            FROM candidat c
            LEFT JOIN notes n ON c.num_anonymat = n.num_anonymat 
            LEFT JOIN livret_scolaire l ON c.numero_table = l.candidat_id
        """)
        candidats = self.cur.fetchall()

        coefficients = {"CF": 2, "ORT": 1, "TSQ": 1, "HG": 2, "MATH": 4, "PC_LV2": 2,
                        "SVT": 2, "ANG1": 2, "ANG2": 1}

        for candidat in candidats:
            (numero_table, Type_candidat, Etat_sportif, Nb_F, EPS, CF, ORT, TSQ, SVT, ANG1, MATH, HG, IC, PC_LV2,
             ANG2, Ep_FAC, moy_6e, moy_5e, moy_4e, moy_3e, nombre_de_fois, num_anonymat) = candidat

            # Génération du numéro d'anonymat si inexistant
            if not num_anonymat:
                num_anonymat = self.generer_anonymat()
                self.cur.execute("UPDATE candidat SET num_anonymat=? WHERE numero_table=?",
                                 (num_anonymat, numero_table))
                self.conn.commit()

            # Calcul de la moyenne du cycle
            moy_6e = moy_6e or 0
            moy_5e = moy_5e or 0
            moy_4e = moy_4e or 0
            moy_3e = moy_3e or 0
            moyennes = list(filter(None, [moy_6e, moy_5e, moy_4e, moy_3e]))
            if moyennes:
                moyenne_cycle = sum(moyennes) / len(moyennes)
            else:
                moyenne_cycle = 0

            # Remplacement des valeurs None par 0
            notes = {"EPS": EPS or 0, "CF": CF or 0, "ORT": ORT or 0, "TSQ": TSQ or 0,
                     "SVT": SVT or 0, "ANG1": ANG1 or 0, "MATH": MATH or 0, "HG": HG or 0,
                     "IC": IC or 0, "PC_LV2": PC_LV2 or 0, "ANG2": ANG2 or 0, "Ep_FAC": Ep_FAC or 0}
            nombre_de_fois = nombre_de_fois or 0

            # RM2 : Bonus/Malus EPS
            bonus_eps = notes["EPS"] - 10

            # Calcul des points totaux avec coefficients
            total_points = sum(notes[matiere] * coef for matiere, coef in coefficients.items()) + bonus_eps

            # RM3 : Bonus pour l'épreuve facultative
            if notes["Ep_FAC"] > 10:
                total_points += (notes["Ep_FAC"] - 10)

            # RM15 : Gestion des candidats inaptes
            if Etat_sportif == "Inapte":
                total_points -= bonus_eps
                notes["Ep_FAC"] = 0

            statut = "En attente"

            if total_points >= 180:
                statut = "Admis"
            elif total_points >= 153:
                if nombre_de_fois < 2 and moyenne_cycle >= 12:
                    if 171 <= total_points < 180:
                        statut = "Repêché 1er Tour"
                    elif 144 <= total_points < 153:
                        statut = "Repêché 2nd Tour"
                else:
                    statut = "2nd Tour"
            elif total_points < 153:
                # Conditions pour le repêchage
                if nombre_de_fois < 2 and moyenne_cycle >= 12:
                    if 144 <= total_points < 153:
                        statut = "Repêché 2nd Tour"
                    else:
                        statut = "Échec"
                else:
                    statut = "Échec"

            # Mise à jour du statut en base de données
            self.cur.execute("UPDATE candidat SET statut=? WHERE num_anonymat=?", (statut, num_anonymat))
            self.conn.commit()
    def generer_anonymat(self):
        """Génère un numéro d’anonymat unique en s'assurant qu'il n'existe pas déjà."""
        while True:
            num_anonymat = random.randint(10000, 99999)
            self.cur.execute("SELECT num_anonymat FROM candidat WHERE num_anonymat = ?", (num_anonymat,))
            if not self.cur.fetchone():
                return num_anonymat

    def fermer_connexion(self):
        """Ferme la connexion à la base de données."""
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    deliberation = Deliberation()
    deliberation.calculer_resultats()
    deliberation.fermer_connexion()
