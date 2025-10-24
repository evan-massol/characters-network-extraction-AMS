import spacy as sp
import networkx as nx
import pandas as pd
from unidecode import unidecode
import os
import re

#-------------------------------------FONCTIONS-------------------------------------



# Charger l'antidictionnaire
def filter_antidict(file):
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)
    
def is_valid_entity(text):
                """Filtre strict pour éliminer les artefacts d'extraction PDF, y compris les tirets Unicode"""
                text = text.strip()
                # Liste des tirets Unicode à filtrer
                tirets_unicode = "-–—―‒‑⁻−"
                # Éliminer les entités qui ne contiennent que des chiffres ou des caractères non-alphabétiques
                if not re.search(r'[a-zA-ZÀ-ÿ]', text):
                    return False
                # Éliminer les entités contenant des tirets Unicode
                if any(tiret in text for tiret in tirets_unicode):
                    return False
                # Éliminer les mots avec des patterns de coupure typiques des PDFs
                if re.search(r"[a-z][A-Z]|[A-Z]{3,}|[a-z]{1,2}'[a-z]{1,2}", text):
                    return False
                # Validation finale: doit ressembler à un nom propre
                if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s]{2,}$', text):
                    return False
                # Filtre anti-dictionnaire
                if unidecode(text.lower()) in anti_words:
                    return False
                return True
    


#------------------------------EXTRACTION DES ENTITES-------------------------------



nlp = sp.load("fr_core_news_lg")

anti_words = filter_antidict('fonctionnels_fr.txt')

books = [('paf', './txt/prelude_a_fondation'),
         ('lca', './txt/les_cavernes_d_acier')
        ]

df_dict = {"ID": [], "graphml": []}

for code_book, filepath in books:
    files = [f for f in os.listdir(filepath) if f.endswith('.txt')] # Récupérer tous les fichiers .txt et trier par numéro de chapitre
    files_sorted = sorted(files, key=lambda x: int(re.search(r'\d+', x).group())) # Trier les fichiers selon le nombre présent dans le nom
    for file in files_sorted:
        chemin_complet = os.path.join(filepath, file)
        num_chapter = int(re.search(r"\d+", file).group())-1
        if os.path.isfile(chemin_complet) and file.endswith('.txt'):

            f = open(chemin_complet, 'r', encoding="utf-8")
            corpus = f.read()
            f.close()

            doc = nlp(corpus)
            LP = []
            LL = []
            LM = []

            for ent in doc.ents:           
                if ent.label_ == "PER" and is_valid_entity(ent.text):
                    LP.append(ent)
                elif ent.label_ == "LOC" and is_valid_entity(ent.text):
                    LL.append(ent)
                elif ent.label_ == "MISC":
                    LM.append(ent)

            # for ent in sorted(set(LP)):
            #     print(f"{ent:<30}{LP.count(ent)}")    #Affiche les entités trouvés

            print(code_book, ", ", file, ", ", num_chapter)
            print("Nombre de personnages détéctés : ", len(set(LP)))
            print("Nombre de lieux détéctés : ", len(set(LL)))
            print("Nombre d'entités non catégorisés : ", len(set(LM)))
            print('\n ---------------------------\n')


            # AJOUTER DE QUOI CHERCHER LES RELATIONS


            # PRETRAITER LE TEXTE



#-------------------------------CREATION DES GRAPHES--------------------------------



            G = nx.Graph()
            for per in set(LP):
                G.add_node(per.text)
                G.nodes[per.text]["names"] = per.text

            df_dict["ID"].append("{}{}".format(code_book, num_chapter))
            graphml = "".join(nx.generate_graphml(G))
            df_dict["graphml"].append(graphml)



#------------------------------EXPORTATION DES GRAPHES------------------------------



df = pd.DataFrame(df_dict)
df.set_index("ID", inplace=True)
df.to_csv("./EvanMASSOL_MartinGERIS.csv")