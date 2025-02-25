import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox
from style import appliquer_theme, styliser_bouton, styliser_label, styliser_entry, styliser_frame, styliser_treeview
from Jury import Jury
from deliberation import Deliberation
from GestionCandidats import Candidat
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Candidats - BFEM")
        self.root.geometry("900x600")

        self.deliberation = Deliberation()

        # Appliquer le thème Bootstrap
        self.style = appliquer_theme(root, theme="superhero")

        # --- Cadre pour les paramètres du Jury ---
        self.frame_jury = ttk.Labelframe(root, text="Paramètres du Jury", padding=10)
        styliser_frame(self.frame_jury)
        self.frame_jury.pack(padx=20, pady=20, fill="x")

        self.creer_formulaire_jury()

        self.stats_label = ttk.Label(self.root, text="Statistiques : ", font=("Helvetica", 12))
        self.stats_label.pack(pady=10)

        # --- Boutons principaux ---
        self.btn_frame = ttk.Frame(root)
        self.btn_frame.pack(pady=10)

        self.btn_deliberation = ttk.Button(self.btn_frame, text="📊 Calculer Résultats",
                                           command=self.calculer_resultats)
        styliser_bouton(self.btn_deliberation, "success")
        self.btn_deliberation.pack(side="left", padx=10)

        self.btn_imprimer_pdf = ttk.Button(self.btn_frame, text="📄 Imprimer PDF", command=self.imprimer_pdf)
        styliser_bouton(self.btn_imprimer_pdf, "info")
        self.btn_imprimer_pdf.pack(side="left", padx=10)

        # --- Tableau (Treeview) pour afficher les résultats ---
        self.frame_treeview = ttk.Frame(root)
        self.frame_treeview.pack(padx=20, pady=10, fill="both", expand=True)

        self.creer_tableau_resultats()

    def creer_formulaire_jury(self):
        """Crée les champs du formulaire pour les paramètres du jury."""

        labels = ["IA (Région)", "IEF (Départements)", "Localité", "Centre d’Examen", "Président de Jury", "Téléphone"]
        self.entries = {}

        for i, label in enumerate(labels):
            row, col = divmod(i, 2)
            lbl = ttk.Label(self.frame_jury, text=label + " :")
            styliser_label(lbl)
            lbl.grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)

            entry = ttk.Entry(self.frame_jury, width=25)
            styliser_entry(entry)
            entry.grid(row=row, column=col * 2 + 1, padx=5, pady=5)
            self.entries[label] = entry

        self.btn_enregistrer_jury = ttk.Button(self.frame_jury, text="💾 Enregistrer Jury",
                                               command=self.enregistrer_jury)
        styliser_bouton(self.btn_enregistrer_jury, "primary")
        self.btn_enregistrer_jury.grid(row=3, column=0, columnspan=4, pady=10)

    def creer_tableau_resultats(self):
        """Crée le tableau pour afficher les résultats des candidats."""
        columns = (
        "Numéro", "Prénom", "Nom", "Date de Naissance", "Lieu de Naissance", "Établissement", "Nombre de fois",
        "Statut")
        self.tree = ttk.Treeview(self.frame_treeview, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=100, anchor="center")

        styliser_treeview(self.tree)
        self.tree.pack(fill="both", expand=True)

    def enregistrer_jury(self):
        """Récupère les paramètres du jury et les enregistre."""
        valeurs = {label: entry.get().strip() for label, entry in self.entries.items()}

        if not all(valeurs.values()):
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs du jury.")
            return

        jury = Jury(valeurs["IA (Région)"], valeurs["IEF (Départements)"], valeurs["Localité"],
                    valeurs["Centre d’Examen"], valeurs["Président de Jury"], valeurs["Téléphone"])

        resultat = jury.enregistrer(self.deliberation)
        if resultat is True:
            messagebox.showinfo("Succès", "Les paramètres du jury ont été enregistrés avec succès.")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.ouvrir_GestionCandidat()
        else:
            messagebox.showerror("Erreur", resultat)

    def calculer_resultats(self):
        self.mettre_a_jour_base()  # Mise à jour des données avant le calcul
        self.deliberation.calculer_resultats()
        self.afficher_resultats()

    def mettre_a_jour_base(self):
        """Met à jour la base de données avant de calculer les résultats."""
        try:
            self.deliberation.cur.execute("""
                UPDATE candidat
                SET statut = 'En cours de traitement'
            """)
            self.deliberation.conn.commit()
            print("Base de données mise à jour avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur de mise à jour", f"Une erreur est survenue : {e}")

    def afficher_resultats(self):
        """Affiche les résultats triés dans le tableau Treeview et met à jour les statistiques."""
        self.deliberation.cur.execute("""
            SELECT numero_table, prenom, nom, date_naissance, lieu_naissance, Etab, Nb_F, statut 
            FROM candidat
        """)
        candidats = self.deliberation.cur.fetchall()

        # Classer les candidats en trois groupes
        admis = [c for c in candidats if c[7] in ("Admis", "Repêché 1er Tour")]
        second_tour = [c for c in candidats if c[7] in ("2nd Tour", "Repêché 2nd Tour")]
        echec = [c for c in candidats if c[7] == "Échec"]

        # Vider le Treeview avant d'insérer les nouvelles valeurs
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Ajouter les candidats classés dans le Treeview
        for cand in admis:
            self.tree.insert("", "end", values=cand, tags=("admis",))
        for cand in second_tour:
            self.tree.insert("", "end", values=cand, tags=("second_tour",))
        for cand in echec:
            self.tree.insert("", "end", values=cand, tags=("echec",))

        # Appliquer des couleurs différentes pour chaque catégorie
        self.tree.tag_configure("admis", background="lightgreen")
        self.tree.tag_configure("second_tour", background="lightyellow")
        self.tree.tag_configure("echec", background="lightcoral")

        # Mettre à jour les statistiques
        total_candidats = len(candidats)
        nb_admis = len(admis)
        nb_second_tour = len(second_tour)
        nb_echec = len(echec)

        if total_candidats > 0:
            pourcentage_admis = (nb_admis / total_candidats) * 100
            pourcentage_second_tour = (nb_second_tour / total_candidats) * 100
            pourcentage_echec = (nb_echec / total_candidats) * 100
        else:
            pourcentage_admis = pourcentage_second_tour = pourcentage_echec = 0

        stats_text = (
            f"Total candidats : {total_candidats}\n"
            f"Admis : {nb_admis} ({pourcentage_admis:.2f}%)\n"
            f"Second Tour : {nb_second_tour} ({pourcentage_second_tour:.2f}%)\n"
            f"Échec : {nb_echec} ({pourcentage_echec:.2f}%)"
        )

        self.stats_label.config(text=stats_text)  # Affichage des statistiques dans l'interface

    def imprimer_pdf(self):
        """Génère un fichier PDF contenant les résultats triés et les statistiques."""
        pdf_file = "resultats_deliberation.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Titre principal du document
        titre = Paragraph("Résultats de la Délibération", styles["Title"])
        elements.append(titre)
        elements.append(Spacer(1, 20))

        # Récupération des paramètres du jury
        try:
            self.deliberation.cur.execute("""
                        SELECT IA, IEF, localite, centre_examen, president_jury, telephone
                        FROM jury
                        ORDER BY rowid DESC LIMIT 1
                    """)
            jury_params = self.deliberation.cur.fetchone()
        except Exception as e:
            jury_params = None

        if jury_params:
            labels = ["IA (Région)", "IEF (Départements)", "Localité", "Centre d’Examen", "Président de Jury",
                      "Téléphone"]
            data_jury = []
            for label, param in zip(labels, jury_params):
                data_jury.append(f"<b>{label}</b> : {param}")
            jury_text = "<br/>".join(data_jury)
        else:
            jury_text = "Aucun paramètre de jury enregistré."

        entete = Paragraph(jury_text, styles["Normal"])
        elements.append(entete)
        elements.append(Spacer(1, 20))


        self.deliberation.cur.execute("""
            SELECT numero_table, prenom, nom, date_naissance, lieu_naissance, Etab, statut 
            FROM candidat
        """)
        candidats = self.deliberation.cur.fetchall()

        # Séparation des candidats en trois groupes
        admis = []
        second_tour = []
        echec = []
        for cand in candidats:
            if cand[6] in ("Admis", "Repêché 1er Tour"):
                admis.append(cand)
            elif cand[6] in ("2nd Tour", "Repêché 2nd Tour"):
                second_tour.append(cand)
            else:
                echec.append(cand)

        total_candidats = len(candidats)
        nb_admis = len(admis)
        nb_second_tour = len(second_tour)
        nb_echec = len(echec)

        if total_candidats > 0:
            pourcentage_admis = (nb_admis / total_candidats) * 100
            pourcentage_second_tour = (nb_second_tour / total_candidats) * 100
            pourcentage_echec = (nb_echec / total_candidats) * 100
        else:
            pourcentage_admis = pourcentage_second_tour = pourcentage_echec = 0

        # Ajouter les statistiques
        stats_text = (
            f"Total candidats : {total_candidats}<br/>"
            f"Admis : {nb_admis} ({pourcentage_admis:.2f}%)<br/>"
            f"Second Tour : {nb_second_tour} ({pourcentage_second_tour:.2f}%)<br/>"
            f"Échec : {nb_echec} ({pourcentage_echec:.2f}%)<br/><br/>"
        )
        elements.append(Paragraph(stats_text, styles["Normal"]))
        elements.append(Spacer(1, 20))

        def ajouter_table(titre, data):
            """Ajoute un tableau au PDF avec un titre."""
            elements.append(Paragraph(titre, styles["Heading2"]))
            elements.append(Spacer(1, 10))
            table_data = [["Numéro", "Prénom", "Nom", "Date de Naissance", "Lieu", "Établissement", "Statut"]]
            table_data.extend(data)

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Ajouter les tableaux triés dans le PDF
        ajouter_table("Liste des Admis", admis)
        ajouter_table("Liste Second Tour", second_tour)
        ajouter_table("Liste des Échecs", echec)

        # Générer le
        doc.build(elements)
        messagebox.showinfo("PDF Généré", f"Les résultats ont été enregistrés dans {pdf_file}")

    def ouvrir_GestionCandidat(self):
        """Ouvre la fenêtre de gestion des candidats."""
        fen = tk.Toplevel(self.root)
        fen.title("Gestion des candidats")
        Candidat(fen)


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = Application(root)
    root.mainloop()
