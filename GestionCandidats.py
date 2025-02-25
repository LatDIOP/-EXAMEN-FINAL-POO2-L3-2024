import tkinter as tk
from tkinter import ttk, messagebox
import random

from Releve import Releve
from base_de_donnees import BaseDeDonnees
from style import appliquer_theme
from Selection import Selection


class Candidat:
    def __init__(self, root):
        """Initialisation de l'interface et connexion à la base de données"""

        frame_conteneur = tk.Frame(root)
        frame_conteneur.pack(padx=10, pady=10)

        self.bdd = BaseDeDonnees()
        self.conn = self.bdd.conn
        self.cur = self.bdd.cur

        self.style = appliquer_theme(root, theme="journal")

        self.selection = Selection()
        self.releve = Releve(root)

        """Interface Candidat"""
        # --- Cadre pour les Champs candidats ---
        """self.frame_candidat = tk.LabelFrame(root, text="Enregistrement des candidats", padx=10, pady=10)
        self.frame_candidat.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")"""

        self.frame_candidat = tk.Frame(frame_conteneur, bd=2, relief=tk.SUNKEN)
        self.frame_candidat.pack(side=tk.LEFT, padx=10, pady=10)
        self.champ_candidat()

        self.frame_notes = tk.Frame(frame_conteneur, bd=2, relief=tk.SUNKEN)
        self.frame_notes.pack(side=tk.LEFT, padx=10, pady=10)
        self.champ_notes()

        # --- Cadre pour le Livret scolaire ---
        self.frame_livret = tk.Frame(frame_conteneur, bd=2, relief=tk.SUNKEN)
        self.frame_livret.pack(side=tk.LEFT, padx=10, pady=10)
        self.champ_livret()

        # --- Cadre pour afficher la liste des candidats ---
        self.frame_affichage = tk.LabelFrame(root, text="Liste des candidats", padx=10, pady=10)
        self.frame_affichage.pack(fill="both", expand=True, padx=10, pady=10)

        # Création du Treeview pour afficher les candidats
        self.creer_treeview()

    def champ_candidat(self):
        """Crée le formulaire d'enregistrement des candidats."""
        labels = ["Numéro Table", "Prénom", "Nom", "Date de Naissance", "Lieu de Naissance", "Sexe",
                  "Nombre de fois", "Type de candidat", "Etablissement", "Nationalité", "Etat Sportif",
                  "Epreuve facultative", "Numéro Anonymat"]

        self.entries = {}

        for i, label in enumerate(labels):
            row, col = divmod(i, 2)
            tk.Label(self.frame_candidat, text=f"{label} :").grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)

            if label in ["Sexe", "Nombre de fois", "Type de candidat", "Etat Sportif", "Epreuve facultative"]:
                values = {
                    "Sexe": ("M", "F"),
                    "Nombre de fois": (1, 2, 3, 4),
                    "Type de candidat": ("Officiel", "Individuel"),
                    "Etat Sportif": ("Apte", "Inapte"),
                    "Epreuve facultative": ("DESSIN", "MUSIQUE", "COUTURE", "NEUTRE")
                }
                entry = ttk.Combobox(self.frame_candidat, values=values[label], state="readonly", width=20)
            else:
                entry = tk.Entry(self.frame_candidat, width=20)

            entry.grid(row=row, column=col * 2 + 1, padx=5, pady=5)
            self.entries[label] = entry

        # Numéro d'anonymat : affiché mais non modifiable (sera généré automatiquement)
        self.entries["Numéro Anonymat"].config(state="readonly")

        # Boutons Ajouter et Afficher
        self.btn_ajouter_candidat = tk.Button(self.frame_candidat, text="Ajouter", command=self.enregistrer_candidat)
        self.btn_ajouter_candidat.grid(row=7, column=0, columnspan=2, pady=10)

        self.btn_ajouter_candidat = tk.Button(self.frame_candidat, text="Modifier", command=self.modifier_candidat)
        self.btn_ajouter_candidat.grid(row=7, column=1, columnspan=2, pady=10)

        self.btn_afficher_candidat = tk.Button(self.frame_candidat, text="Supprimer", command=self.supprimer_candidat)
        self.btn_afficher_candidat.grid(row=7, column=2, columnspan=2, pady=10)

        self.btn_afficher_candidat = tk.Button(self.frame_candidat, text="Afficher", command=self.affich_candidat)
        self.btn_afficher_candidat.grid(row=7, column=3, columnspan=2, pady=10)

    def enregistrer_candidat(self):
        data = {}
        data['candidat'] = {label: entry.get().strip() for label, entry in self.entries.items()}

        try:
            self.selection.enregistrer_candidat(data)
            messagebox.showinfo("Succès", "Enregistrement effectué avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")

    def modifier_candidat(self):
        """Modifie un candidat existant dans la base de données."""
        numero_table = self.entries["Numéro Table"].get().strip()

        if not numero_table:
            messagebox.showwarning("Champs manquants", "Veuillez entrer le numéro de table du candidat à modifier.")
            return

        data = {label: entry.get().strip() for label, entry in self.entries.items()}

        try:
            result = self.selection.modifier_candidat(numero_table, data)  # Appel à la méthode dans Selection
            if result:
                messagebox.showinfo("Succès", "Le candidat a été modifié avec succès.")
                self.affich_candidat()  # Rafraîchir la liste des candidats
            else:
                messagebox.showerror("Erreur", "La modification du candidat a échoué.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification du candidat : {e}")

    def supprimer_candidat(self):
        """Supprime un candidat et toutes ses données associées (notes et livret) en se basant sur son numéro de table."""
        numero_table = self.entries["Numéro Table"].get().strip()

        if not numero_table:
            messagebox.showwarning("Champs manquants", "Veuillez saisir le numéro de table du candidat à supprimer.")
            return

        if messagebox.askyesno("Confirmation",
                               "Voulez-vous vraiment supprimer ce candidat et toutes ses données associées ?"):
            try:
                result = self.selection.supprimer_candidat(numero_table)  # Appel à la méthode dans Selection
                if result:
                    messagebox.showinfo("Succès", "Candidat et toutes ses données ont été supprimés.")
                    self.affich_candidat()  # Rafraîchir la liste des candidats
                else:
                    messagebox.showerror("Erreur", "La suppression du candidat a échoué.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression du candidat : {e}")

    def affich_candidat(self):
        """Affiche les candidats enregistrés dans le Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT numero_table, prenom, nom, date_naissance, lieu_naissance, sexe, Nb_F, 
                   Type_candidat, Etab, nationalite, Etat_sportif, epreuve_facultative, num_anonymat, statut
            FROM candidat
        """
        self.cur.execute(query)
        candidats = self.cur.fetchall()

        for cand in candidats:
            self.tree.insert("", "end", values=cand)


    def creer_treeview(self):
        """Crée le tableau pour afficher les candidats."""
        columns = ["Numero", "Prenom", "Nom", "Date", "Lieu", "Sexe", "NbF", "Type", "Etab", "Nationalite", "Etat", "Epreuve", "Anonymat"]
        self.tree = ttk.Treeview(self.frame_affichage, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

    def champ_notes(self):
        """Crée le formulaire pour saisir les notes du candidat."""
        labels = ["Anonymat", "Note EPS", "Note Français", "Note Dictée", "Note TSQ", "Note SVT",
                  "Note Anglais", "Note Maths", "Note Histo Géo", "Note IC", "Note LV2",
                  "Note Oral", "Note Epreuve fac"]

        self.entries_notes = {}

        for i, label in enumerate(labels):
            # On utilise divmod pour disposer les widgets sur deux colonnes (modifiez selon vos préférences)
            row, col = divmod(i, 2)
            tk.Label(self.frame_notes, text=f"{label} :").grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)

            # Tous les champs sont modifiables par l'utilisateur
            entry = tk.Entry(self.frame_notes, width=20)
            entry.grid(row=row, column=col * 2 + 1, padx=5, pady=5)
            self.entries_notes[label] = entry

        self.btn_enregistrer_notes = tk.Button(self.frame_notes, text="Enregistrer Notes",
                                               command=self.enregistrer_notes)
        self.btn_enregistrer_notes.grid(row=7, column=0, columnspan=2, pady=10)

        self.btn_afficher_releve = tk.Button(self.frame_notes, text="Afficher Relevé", command=self.afficher_releve_candidat)
        self.btn_afficher_releve.grid(row=7, column=2, columnspan=2, pady=10)

        # Bouton Imprimer Relevé
        self.btn_imprimer_releve = tk.Button(self.frame_notes, text="Imprimer Relevé", command=self.imprimer_releve)
        self.btn_imprimer_releve.grid(row=7, column=4, columnspan=2, pady=10)

    def afficher_releve_candidat(self):
        # Récupérer le numéro d'anonymat depuis le formulaire
        num_anonymat = self.entries_notes["Anonymat"].get().strip()
        if not num_anonymat:
            messagebox.showwarning("Erreur", "Veuillez entrer un numéro d'anonymat.")
            return

        try:
            self.releve.afficher_releve(num_anonymat)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher le relevé : {e}")
    def imprimer_releve(self):
        pass

    def enregistrer_notes(self):
        """Enregistre ou met à jour les notes d'un candidat en appelant la méthode de Selection."""
        num_anonymat = self.entries_notes["Anonymat"].get().strip()

        if not num_anonymat:
            messagebox.showwarning("Erreur", "Veuillez entrer un numéro d'anonymat.")
            return

        # Récupérer les notes saisies
        notes = {label: self.entries_notes[label].get().strip() for label in self.entries_notes if label != "Anonymat"}

        try:
            # Convertir les notes en float (valider les entrées)
            notes = {label: float(value) if value else 0 for label, value in notes.items()}
        except ValueError:
            messagebox.showerror("Erreur", "Toutes les notes doivent être des nombres valides.")
            return

        try:
            # Appel à la fonction `enregistrer_notes()` dans Selection
            self.selection.enregistrer_notes(num_anonymat, notes)
            messagebox.showinfo("Succès", "Les notes ont été enregistrées avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des notes : {e}")

    def champ_livret(self):
        """Crée le formulaire pour saisir les informations du livret scolaire."""
        labels = ["Numéro Table", "moy_6e", "moy_5e", "moy_4e", "moy_3e"]
        self.entries_livret = {}

        tk.Label(self.frame_livret, text="--- Livret Scolaire ---", font=("Arial", 12, "bold")).pack(pady=5)

        for label in labels:
            frame = tk.Frame(self.frame_livret)
            frame.pack(padx=5, pady=5, fill="x")

            tk.Label(frame, text=f"{label} :", width=15, anchor="e").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=20)
            entry.pack(side=tk.LEFT, padx=5)
            self.entries_livret[label] = entry

            # Boutons
        self.btn_enregistrer_livret = tk.Button(self.frame_livret, text="Enregistrer Livret",
                                                command=self.enregistrer_livret)
        self.btn_enregistrer_livret.pack(pady=5)
        self.btn_modifier_livret = tk.Button(self.frame_livret, text="Modifier Livret",
                                                 command=self.modifier_livret)
        self.btn_modifier_livret.pack(pady=5)

    def enregistrer_livret(self):
        """Appelle Selection pour enregistrer un livret scolaire."""
        candidat_id = self.entries_livret["Numéro Table"].get().strip()
        if not candidat_id:
            messagebox.showwarning("Champs manquants", "Veuillez saisir le numéro de table du candidat.")
            return

        try:
            # Récupérer et formater les données du livret
            data = {label: self.entries_livret[label].get().strip() for label in self.entries_livret if
                    label != "Numéro Table"}

            # Appel à `enregistrer_livret()` dans `Selection`
            result = self.selection.enregistrer_livret(candidat_id, data)

            if result:
                messagebox.showinfo("Succès", "Livret scolaire enregistré avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def modifier_livret(self):
        """Appelle Selection pour modifier un livret scolaire."""
        candidat_id = self.entries_livret["Numéro Table"].get().strip()
        if not candidat_id:
            messagebox.showwarning("Champs manquants", "Veuillez saisir le numéro de table du candidat.")
            return

        try:
            # Récupérer et formater les données du livret
            data = {label: self.entries_livret[label].get().strip() for label in self.entries_livret if
                    label != "Numéro Table"}

            # Appel à `modifier_livret()` dans `Selection`
            result = self.selection.modifier_livret(candidat_id, data)

            if result:
                messagebox.showinfo("Succès", "Livret scolaire mis à jour avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


    def fermer_connexion(self):
        """Ferme la connexion à la base de données."""
        self.bdd.fermer_connexion()


# Test du module
if __name__ == "__main__":
    root = tk.Tk()
    app = Candidat(root)
    root.mainloop()
