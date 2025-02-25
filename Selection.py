from tkinter import messagebox
from base_de_donnees import BaseDeDonnees
import random


class Selection:
    def __init__(self):
        self.bdd = BaseDeDonnees()
        self.conn = self.bdd.conn
        self.cur = self.bdd.cur

    def generer_numero_anonymat(self):
        """Génère un numéro d’anonymat unique."""
        while True:
            num_anonymat = random.randint(10000, 99999)
            self.cur.execute("SELECT num_anonymat FROM candidat WHERE num_anonymat = ?", (num_anonymat,))
            if not self.cur.fetchone():
                return num_anonymat

    def enregistrer_candidat(self, data):
        """Ajoute un candidat dans la base avec un numéro d’anonymat unique."""
        valeurs = {label: value.strip() for label, value in data['candidat'].items()}
        valeurs.pop("Numéro Anonymat")

        if not all(valeurs.values()):
            raise Exception("Veuillez remplir tous les champs du candidat.")

        num_anonymat = self.generer_numero_anonymat()

        query = '''
            INSERT INTO candidat (numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, 
            Nb_F, Type_candidat, Etab, nationalite, Etat_sportif, epreuve_facultative, statut, num_anonymat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            self.cur.execute(query, (
                valeurs["Numéro Table"], valeurs["Prénom"], valeurs["Nom"], valeurs["Date de Naissance"],
                valeurs["Lieu de Naissance"], valeurs["Sexe"], valeurs["Nombre de fois"], valeurs["Type de candidat"],
                valeurs["Etablissement"], valeurs["Nationalité"], valeurs["Etat Sportif"],
                valeurs["Epreuve facultative"], "En attente", num_anonymat
            ))
            self.conn.commit()
        except Exception as e:
            raise Exception(f"Erreur lors de l'ajout : {e}")

    def modifier_candidat(self, numero_table, data):
        """Met à jour les informations d'un candidat dans la base de données."""
        try:
            query = """
                UPDATE candidat 
                SET prenom=?, nom=?, date_naissance=?, lieu_naissance=?, sexe=?, Nb_F=?, 
                    Type_candidat=?, Etab=?, nationalite=?, Etat_sportif=?, epreuve_facultative=? 
                WHERE numero_table=?
            """
            valeurs = (
                data["Prénom"], data["Nom"], data["Date de Naissance"], data["Lieu de Naissance"],
                data["Sexe"], data["Nombre de fois"], data["Type de candidat"], data["Etablissement"],
                data["Nationalité"], data["Etat Sportif"], data["Epreuve facultative"], numero_table
            )
            self.cur.execute(query, valeurs)
            self.conn.commit()
            return True
        except Exception as e:
            print("Erreur lors de la modification du candidat :", e)
            return False

    def supprimer_candidat(self, numero_table):
        """Supprime un candidat et toutes ses données associées (notes et livret)."""
        try:
            # Récupérer num_anonymat avant suppression
            self.cur.execute("SELECT num_anonymat FROM candidat WHERE numero_table=?", (numero_table,))
            result = self.cur.fetchone()
            if not result:
                return False
            num_anonymat = result[0]

            # Supprimer les données associées
            self.cur.execute("DELETE FROM notes WHERE num_anonymat=?", (num_anonymat,))
            self.cur.execute("DELETE FROM livret_scolaire WHERE candidat_id=?", (numero_table,))
            self.cur.execute("DELETE FROM candidat WHERE numero_table=?", (numero_table,))

            self.conn.commit()
            return True
        except Exception as e:
            print("Erreur lors de la suppression du candidat :", e)
            return False

    def enregistrer_notes(self, num_anonymat, notes):
        """Insère ou met à jour les notes d'un candidat en se basant sur num_anonymat."""
        self.cur.execute("SELECT num_anonymat FROM candidat WHERE num_anonymat = ?", (num_anonymat,))
        if not self.cur.fetchone():
            messagebox.showerror("Erreur", "Le numéro d'anonymat saisi n'existe pas.")
            return

        # Vérifier si des notes existent déjà
        self.cur.execute("SELECT num_anonymat FROM notes WHERE num_anonymat = ?", (num_anonymat,))
        result = self.cur.fetchone()

        if result:
            # Mise à jour des notes existantes
            query = '''
                UPDATE notes SET EPS=?, CF=?, ORT=?, TSQ=?, SVT=?, ANG1=?, MATH=?, HG=?, IC=?, 
                PC_LV2=?, ANG2=?, Ep_FAC=? WHERE num_anonymat=?
            '''
            valeurs = (
                notes["Note EPS"], notes["Note Français"], notes["Note Dictée"], notes["Note TSQ"],
                notes["Note SVT"], notes["Note Anglais"], notes["Note Maths"], notes["Note Histo Géo"],
                notes["Note IC"], notes["Note LV2"], notes["Note Oral"], notes["Note Epreuve fac"],
                num_anonymat
            )
        else:
            # Insérer de nouvelles notes
            query = '''
                INSERT INTO notes (num_anonymat, EPS, CF, ORT, TSQ, SVT, ANG1, MATH, HG, IC, PC_LV2, ANG2, Ep_FAC)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            valeurs = (
                num_anonymat, notes["Note EPS"], notes["Note Français"], notes["Note Dictée"], notes["Note TSQ"],
                notes["Note SVT"], notes["Note Anglais"], notes["Note Maths"], notes["Note Histo Géo"],
                notes["Note IC"], notes["Note LV2"], notes["Note Oral"], notes["Note Epreuve fac"]
            )

        try:
            self.cur.execute(query, valeurs)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des notes : {e}")

    def enregistrer_livret(self, candidat_id, data):
        """Insère les informations du livret scolaire pour un candidat."""
        try:
            # Vérifier si le candidat existe
            self.cur.execute("SELECT Nb_F FROM candidat WHERE numero_table = ?", (candidat_id,))
            result = self.cur.fetchone()

            if not result:
                raise Exception("Aucun candidat trouvé avec ce numéro de table.")

            nombre_de_fois = result[0]

            # Vérifier si un livret existe déjà
            self.cur.execute("SELECT candidat_id FROM livret_scolaire WHERE candidat_id = ?", (candidat_id,))
            if self.cur.fetchone():
                raise Exception("Un livret existe déjà pour ce candidat. Utilisez 'Modifier Livret'.")

            # Insertion du livret avec `nombre_de_fois`
            query = """
                INSERT INTO livret_scolaire (candidat_id, moy_6e, moy_5e, moy_4e, moy_3e, nombre_de_fois) 
                VALUES (?, ?, ?, ?, ?, ?)
            """
            valeurs = (candidat_id, float(data["moy_6e"]), float(data["moy_5e"]),
                       float(data["moy_4e"]), float(data["moy_3e"]), nombre_de_fois)

            self.cur.execute(query, valeurs)
            self.conn.commit()
            return True

        except ValueError:
            raise Exception("Les moyennes doivent être des nombres valides.")
        except Exception as e:
            raise Exception(f"Erreur lors de l'enregistrement du livret : {e}")

    def modifier_livret(self, candidat_id, data):
        """Met à jour les informations du livret scolaire d'un candidat."""
        try:
            # Vérifier si le livret existe
            self.cur.execute("SELECT candidat_id FROM livret_scolaire WHERE candidat_id = ?", (candidat_id,))
            if not self.cur.fetchone():
                raise Exception("Aucun livret trouvé pour ce candidat. Utilisez 'Enregistrer Livret'.")

            # Mise à jour du livret
            query = """
                UPDATE livret_scolaire 
                SET moy_6e = ?, moy_5e = ?, moy_4e = ?, moy_3e = ? 
                WHERE candidat_id = ?
            """
            valeurs = (float(data["moy_6e"]), float(data["moy_5e"]), float(data["moy_4e"]),
                       float(data["moy_3e"]), candidat_id)

            self.cur.execute(query, valeurs)
            self.conn.commit()
            return True

        except ValueError:
            raise Exception("Les moyennes doivent être des nombres valides.")
        except Exception as e:
            raise Exception(f"Erreur lors de la modification du livret : {e}")
