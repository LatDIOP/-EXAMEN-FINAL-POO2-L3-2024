import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
from base_de_donnees import BaseDeDonnees  # Assurez-vous que la connexion à la base est correcte
from datetime import datetime

class Releve:
    def __init__(self, root):
        self.root = root
        self.bdd = BaseDeDonnees()  # Connexion à la base de données
        self.conn = self.bdd.conn
        self.cur = self.bdd.cur

    def obtenir_releve(self, num_anonymat):
        """
        Récupère les informations d'un candidat et ses notes à partir de son num_anonymat.
        """
        self.cur.execute("""
            SELECT c.prenom, c.nom, c.date_naissance, c.lieu_naissance, c.Etab, 
                   c.numero_table, c.Nb_F, c.sexe, c.nationalite, c.Type_candidat, 
                   n.EPS, n.CF, n.ORT, n.TSQ, n.SVT, n.ANG1, n.MATH, n.HG, n.IC, n.PC_LV2, n.ANG2, n.Ep_FAC,
                   c.statut
            FROM candidat c
            JOIN notes n ON c.num_anonymat = n.num_anonymat
            WHERE c.num_anonymat = ?
        """, (num_anonymat,))
        candidat = self.cur.fetchone()
        if candidat:
            # Les notes se trouvent à partir de l'indice 10 jusqu'à 21 ici
            moyenne = self.calculer_moyenne(candidat[10:22])
            return candidat, moyenne
        else:
            raise ValueError("Candidat non trouvé")

    def calculer_moyenne(self, notes):
        """Calcule la moyenne pondérée à partir des notes et coefficients."""
        coefficients = [1, 2, 1, 1, 2, 2, 4, 2, 1, 2, 1]
        total_notes = sum(note * coeff for note, coeff in zip(notes, coefficients))
        total_coefficients = sum(coefficients)
        return total_notes / total_coefficients if total_coefficients > 0 else 0

    def afficher_releve(self, num_anonymat):
        """
        Affiche le relevé de notes pour un candidat dans une nouvelle fenêtre.
        Le num_anonymat est fourni en argument.
        """
        if not num_anonymat:
            messagebox.showwarning("Champs manquants", "Veuillez entrer un numéro d'anonymat.")
            return
        try:
            candidat, moyenne = self.obtenir_releve(num_anonymat)
            self.afficher_releve_frame(candidat, moyenne)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage du relevé : {e}")

    def afficher_releve_frame(self, candidat, moyenne):

        frame_releve = tk.Toplevel(self.root)
        frame_releve.title("Relevé de Notes")

        # --- Bloc informations du candidat ---
        info_frame = tk.Frame(frame_releve)
        info_frame.pack(fill="x", padx=10, pady=5)

        left_info = tk.Frame(info_frame)
        left_info.grid(row=0, column=0, sticky="w", padx=5)
        right_info = tk.Frame(info_frame)
        right_info.grid(row=0, column=1, sticky="e", padx=5)

        # À gauche (indices supposés) :
        # candidat[0]: prénom, candidat[1]: nom, [2]: date, [3]: lieu, [4]: centre d'examen, [5]: numéro table.
        tk.Label(left_info, text=f"{candidat[0]} {candidat[1]}", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(left_info, text=f"Date: {candidat[2]}    Lieu: {candidat[3]}").grid(row=1, column=0, sticky="w")
        tk.Label(left_info, text=f"Centre d'examen: {candidat[4]}    Numéro Table: {candidat[5]}").grid(row=2, column=0, sticky="w")

        # À droite :
        # candidat[6]: nombre de fois, [7]: sexe, [8]: nationalité, [9]: type de candidat.
        tk.Label(right_info, text=f"Nombre de fois: {candidat[6]}    Sexe: {candidat[7]}", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="e")
        tk.Label(right_info, text=f"Nationalité: {candidat[8]}").grid(row=1, column=0, sticky="e")
        tk.Label(right_info, text=f"Type de candidat: {candidat[9]}").grid(row=2, column=0, sticky="e")

        # --- Tableau des épreuves écrites ---
        tableau_frame = tk.LabelFrame(frame_releve, text="Tableau des Épreuves Écrites", padx=10, pady=10)
        tableau_frame.pack(fill="both", padx=10, pady=5)

        # Définition des matières et coefficients (à adapter si besoin)
        matieres = ["EPS", "CF", "ORT", "TSQ", "SVT", "ANG1", "MATH", "HG", "IC", "PC_LV2", "ANG2", "Ep_FAC"]
        coefficients = [1, 2, 1, 1, 2, 2, 4, 2, 1, 2, 1, 1]
        # Les notes se trouvent à partir de l'indice 10 jusqu'à 21
        notes = candidat[10:22]

        # En-têtes globaux
        tk.Label(tableau_frame, text="Épreuves écrites", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=0, column=0, columnspan=2, sticky="nsew")
        tk.Label(tableau_frame, text="Résultats", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=0, column=2, columnspan=3, sticky="nsew")
        # Sous-en-têtes
        tk.Label(tableau_frame, text="Matière", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=1, column=0, sticky="nsew")
        tk.Label(tableau_frame, text="Coef", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=1, column=1, sticky="nsew")
        tk.Label(tableau_frame, text="Note", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=1, column=2, sticky="nsew")
        tk.Label(tableau_frame, text="Points obtenus", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=1, column=3, sticky="nsew")
        tk.Label(tableau_frame, text="Total (max)", font=("Arial", 10, "bold"), borderwidth=1, relief="solid")\
            .grid(row=1, column=4, sticky="nsew")

        total_points_obtenus = 0
        total_points_max = 0
        for i, (matiere, coef) in enumerate(zip(matieres, coefficients)):
            row = i + 2
            tk.Label(tableau_frame, text=matiere, borderwidth=1, relief="solid")\
                .grid(row=row, column=0, sticky="nsew", padx=1, pady=1)
            tk.Label(tableau_frame, text=str(coef), borderwidth=1, relief="solid")\
                .grid(row=row, column=1, sticky="nsew", padx=1, pady=1)
            note = float(notes[i]) if i < len(notes) and notes[i] != None else 0
            tk.Label(tableau_frame, text=str(note), borderwidth=1, relief="solid")\
                .grid(row=row, column=2, sticky="nsew", padx=1, pady=1)
            points_obtenus = note * coef
            total_points_obtenus += points_obtenus
            tk.Label(tableau_frame, text=f"{points_obtenus:.2f}", borderwidth=1, relief="solid")\
                .grid(row=row, column=3, sticky="nsew", padx=1, pady=1)
            total_max = 20 * coef
            total_points_max += total_max
            tk.Label(tableau_frame, text=str(total_max), borderwidth=1, relief="solid")\
                .grid(row=row, column=4, sticky="nsew", padx=1, pady=1)

        # --- Totaux et moyenne globale ---
        totaux_frame = tk.Frame(frame_releve)
        totaux_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(totaux_frame, text=f"Total points obtenus : {total_points_obtenus:.2f} / {total_points_max}",
                 font=("Arial", 10, "bold")).pack(side="left", anchor="w")
        moyenne_sur_20 = (total_points_obtenus / total_points_max) * 20 if total_points_max > 0 else 0
        tk.Label(totaux_frame, text=f"Moyenne globale : {moyenne_sur_20:.2f} / 20",
                 font=("Arial", 10, "bold")).pack(side="right", anchor="e")

        # --- Décision du jury ---
        # On suppose que le statut (la décision du jury) est à l'indice 22 dans le tuple (à adapter)
        decision = candidat[22] if len(candidat) > 22 else "Non défini"
        decision_frame = tk.Frame(frame_releve)
        decision_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(decision_frame, text=f"Décision du jury à l'issue du 1er tour : {decision}",
                 font=("Arial", 10, "bold")).pack(anchor="w")

        # --- Pied de page ---
        pied_frame = tk.Frame(frame_releve)
        pied_frame.pack(fill="x", padx=10, pady=10)
        IA_jury = self.obtenir_IA_jury()
        date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
        tk.Label(pied_frame, text=f"Fait à {IA_jury} le {date_aujourdhui}", font=("Arial", 10))\
            .pack(side="left", anchor="w")

        president_jury = self.obtenir_IA_jury()
        tk.Label(pied_frame, text=f"LE PRESIDENT DU JURY {president_jury}", font=("Arial", 10, "bold"))\
            .pack(side="right", anchor="e")

    def obtenir_IA_jury(self):
        self.cur.execute("SELECT IA, president_jury FROM jury")
        result = self.cur.fetchone()
        return result[0] if result else "Non défini"
