import tkinter as tk
from deliberation import Deliberation
from GestionCandidats import Candidat

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion BFEM")

        self.candidat = Candidat()
        self.deliberation = Deliberation()

        # Bouton pour lancer la délibération
        self.btn_deliberation = tk.Button(root, text="Calculer Résultats", command=self.calculer_resultats)
        self.btn_deliberation.grid(row=7, columnspan=2)

        # Liste des résultats
        self.liste_resultats = tk.Listbox(root, width=50)
        self.liste_resultats.grid(row=8, columnspan=2)

    def calculer_resultats(self):
        """Calcule les résultats et affiche les statuts."""
        self.deliberation.calculer_resultats()
        self.afficher_resultats()

    def afficher_resultats(self):
        """Affiche les résultats des candidats."""
        self.liste_resultats.delete(0, tk.END)
        self.deliberation.cur.execute("SELECT numero_table, prenom, nom, statut FROM candidat")
        candidats = self.deliberation.cur.fetchall()

        for cand in candidats:
            self.liste_resultats.insert(tk.END, f"{cand[0]} {cand[1]} - {cand[2]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
