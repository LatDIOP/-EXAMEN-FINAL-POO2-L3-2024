from base_de_donnees import BaseDeDonnees

class Jury:
    def __init__(self, IA, IEF, localite, centre_examen, president_jury, telephone):
        """Initialisation des attributs du jury."""
        self.IA = IA
        self.IEF = IEF
        self.localite = localite
        self.centre_examen = centre_examen
        self.president_jury = president_jury
        self.telephone = telephone

    def enregistrer(self,deliberation):
        """Enregistre les informations du jury dans la base de données centralisée."""
        bdd = BaseDeDonnees()

        try:
            bdd.cur.execute("""
                INSERT INTO jury (IA, IEF, localite, centre_examen, president_jury, telephone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.IA, self.IEF, self.localite, self.centre_examen, self.president_jury, self.telephone))

            bdd.conn.commit()
            bdd.fermer_connexion()  # Fermer la connexion après l'enregistrement
            return True
        except Exception as e:
            return f"Erreur lors de l'enregistrement du jury : {e}"
