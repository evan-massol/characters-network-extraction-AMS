import json
import os

import numpy as np
import pandas as pd
import networkx as nx


# FUNCTIONS


def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def find_closest_reference(vector, references):
    max_sim = -1
    closest_ref = None
    for name, ref_vec in references.items():
        sim = cosine_similarity(vector, ref_vec)
        if sim > max_sim:
            max_sim = sim
            closest_ref = name
    return closest_ref, max_sim


# INITIALIZATION & INSTANCIATION


input_file = "./json/reference_embeddings_to_categorizing_relations.json"
repertoire = "./csv"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)


# BUILDING OF REFERENCE VECTORS


embedding_ref = {
    "professionnal": 0,
    "friendly": 0,
    "romance": 0
}

for relation, categories in data.items():
    embeddings_resume = []
    for category, embeddings in categories.items():
        embeddings_resume.append(np.mean(embeddings, axis=0))
    embedding_ref[relation] = np.mean(embeddings_resume, axis=0)


# PROCESSING


for file in os.listdir(repertoire):
    if file.endswith(".csv"):
        print(f"Processing {os.path.splitext(file)[0]}...")

        # REBUILDING GRAPH
        df = pd.read_csv(repertoire +"/"+ file, index_col="ID")
        graphml_str = df.loc["Fondation", "graphml"]
        G = nx.parse_graphml(graphml_str)

        # CONTEXTUALISATION
        for u, v, attr in G.edges(data=True):
            contextual_embeddings = json.loads(attr.get("context", "[]"))

            # listprint(embedding_ref)
            context, distance = find_closest_reference(contextual_embeddings, embedding_ref)

            G.edges[u, v]["context"] = json.dumps(context)
        
        graphml_updated = "".join(nx.generate_graphml(G))
        df.loc["Fondation", "graphml"] = graphml_updated
        df.to_csv(f"./csv/processed_relation/{os.path.splitext(file)[0]}.csv")

        # TODO
        # Finir gestion des relations dans le fichier (nombre de relation + pourcentage de relation dans tel ou tel catégorie)
        # Push pour permettre à evan de faire graphe
        # Lancer programme sur gros pc (avec fonction puissante) 
