import sqlite3
import pandas as pd
import random

class BaseDeDonnees:
    def __init__(self, db_name="bfem.db", excel_file="BD_BFEM.xlsx"):
        """Initialise la connexion à la base de données et crée les tables."""
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.excel_file = excel_file
        self.create_tables()

    def create_tables(self):
        """Crée les tables si elles n'existent pas."""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS candidat (
                numero_table INTEGER PRIMARY KEY,
                prenom TEXT,
                nom TEXT,
                date_naissance TEXT,
                lieu_naissance TEXT,
                sexe TEXT,
                Nb_F TEXT,
                Type_candidat TEXT,
                Etab TEXT,
                nationalite TEXT,
                Etat_sportif TEXT,
                epreuve_facultative TEXT,
                statut TEXT DEFAULT 'En attente',
                num_anonymat INTEGER UNIQUE            )
        ''')

        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                numero_table INTEGER,
                EPS REAL,
                CF REAL,
                ORT REAL,
                TSQ REAL,
                SVT REAL,
                ANG1 REAL,
                MATH REAL,
                HG REAL,
                IC REAL,
                PC_LV2 REAL,
                ANG2 REAL,
                Ep_FAC REAL,
                num_anonymat INTEGER UNIQUE,
        FOREIGN KEY (numero_table) REFERENCES candidat(numero_table)
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS livret_scolaire (
                candidat_id INTEGER PRIMARY KEY,
                moy_6e REAL,
                moy_5e REAL,
                moy_4e REAL,
                moy_3e REAL,
                nombre_de_fois INTEGER,
                FOREIGN KEY (candidat_id) REFERENCES candidat(num_anonymat)
            )
        ''')

        self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS jury (
                        IA TEXT,
                        IEF TEXT,
                        localite TEXT,
                        centre_examen TEXT,
                        president_jury TEXT,
                        telephone INTEGER UNIQUE
                        )
                ''')

        self.conn.commit()

    def importer_donnees_excel(self):
        """Importe les données depuis BD_BFEM.xlsx et les insère dans la base."""
        df = pd.read_excel(self.excel_file)

        df.rename(columns={
            'N° de table': 'numero_table',
            'Prenom (s)': 'prenom',
            'NOM': 'nom',
            'Date de nais.': 'date_naissance',
            'Lieu de nais.': 'lieu_naissance',
            'Sexe': 'sexe',
            'Nb fois': 'Nb_F',
            'Type de candidat': 'Type_candidat',
            'Etablissement': 'Etab',
            'Nationnallité': 'nationalite',
            'Etat Sportif': 'Etat_sportif',
            'Epreuve Facultative': 'epreuve_facultative',
            'Moy_6e': 'moy_6e',
            'Moy_5e': 'moy_5e',
            'Moy_4e': 'moy_4e',
            'Moy_3e': 'moy_3e',
            'Note EPS': 'EPS',
            'Note CF': 'CF',
            'Note Ort': 'ORT',
            'Note TSQ': 'TSQ',
            'Note SVT': 'SVT',
            'Note ANG1': 'ANG1',
            'Note MATH': 'MATH',
            'Note HG': 'HG',
            'Note IC': 'IC',
            'Note PC/LV2': 'PC_LV2',
            'Note ANG2': 'ANG2',
            'Note Ep Fac': 'Ep_FAC'
        }, inplace=True)

        for _, row in df.iterrows():
            row['date_naissance'] = str(row['date_naissance'])
            self.cur.execute("""
                   INSERT OR IGNORE INTO candidat (
                       numero_table, prenom, nom, date_naissance, lieu_naissance, sexe,
                       Nb_F, Type_candidat, Etab, nationalite, Etat_sportif, epreuve_facultative, statut
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """, (
                row['numero_table'], row['prenom'], row['nom'], row['date_naissance'], row['lieu_naissance'],
                row['sexe'], row['Nb_F'], row['Type_candidat'], row['Etab'], row['nationalite'], row['Etat_sportif'],
                row['epreuve_facultative'], "En attente"
            ))

            self.cur.execute("""
                   INSERT OR IGNORE INTO notes (
                       numero_table, EPS, CF, ORT, TSQ, SVT, ANG1, MATH, HG, IC, PC_LV2, ANG2, Ep_FAC, num_anonymat
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """, (
                row['numero_table'], row['EPS'], row['CF'], row['ORT'], row['TSQ'], row['SVT'], row['ANG1'],
                row['MATH'], row['HG'], row['IC'], row['PC_LV2'], row['ANG2'], row['Ep_FAC'],
                random.randint(10000, 99999)
            ))

            self.cur.execute("""
                       INSERT OR IGNORE INTO livret_scolaire (
                           candidat_id, moy_6e, moy_5e, moy_4e, moy_3e, nombre_de_fois
                       ) VALUES (?, ?, ?, ?, ?, ?)
                   """, (
                row['numero_table'], row['moy_6e'], row['moy_5e'], row['moy_4e'], row['moy_3e'], row['Nb_F']
            ))

        self.conn.commit()
    def fermer_connexion(self):
        """Ferme la connexion à la base de données."""
        self.cur.close()
        self.conn.close()

# Test du module
if __name__ == "__main__":
    bdd = BaseDeDonnees()
    bdd.importer_donnees_excel()
    bdd.fermer_connexion()
