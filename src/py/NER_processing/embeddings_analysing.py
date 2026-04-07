import json
import numpy as np
from itertools import combinations, product



# FONCTIONS



def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def euclidean_distance(v1, v2):
    return np.linalg.norm(v1 - v2)



# DECLARATIONS ET INSTANCIATIONS



input_file = "./json/reference_embeddings_to_categorizing_relations.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)



# ANALYSES



print("\n===== DISTANCES INTER-CLASSES category =====")

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

vectors = []
vectors.append(("professionnal", embedding_ref["professionnal"]))
vectors.append(("friendly", embedding_ref["friendly"]))
vectors.append(("romance", embedding_ref["romance"]))

for v1, v2 in combinations(vectors, 2):
    eucl = euclidean_distance(v1[1], v2[1])
    cosine = cosine_similarity(v1[1], v2[1])
    print(f"   {v1[0]} {v2[0]} : \n Distance euclidienne : {eucl} \n Similarité cosinus : {cosine}")



vectors = {}
for category, pos_dict in data.items():

    merged = []

    for pos, vecs in pos_dict.items():
        for v in vecs:
            merged.append(np.array([float(x) for x in v]))

    vectors[category] = merged
print("\n===== DISTANCES INTER-CLASSES words =====")

for category, vecs in vectors.items():

    euclidian = []
    cosine = []

    for v1, v2 in combinations(vecs, 2):
        euclidian.append(euclidean_distance(v1, v2))
        cosine.append(cosine_similarity(v1, v2))

    if euclidian:
        print(f"\n{category}")
        print(f"Distance euclidienne moyenne : {np.mean(euclidian)}")
        print(f"Similarité cosinus moyenne : {np.mean(cosine)}")

print("\n===== DISTANCES INTRA-CLASSE words =====")

for cat1, cat2 in combinations(vectors.keys(), 2):

    euclidian = []
    cosine = []

    for v1 in vectors[cat1]:
        for v2 in vectors[cat2]:

            euclidian.append(euclidean_distance(v1, v2))
            cosine.append(cosine_similarity(v1, v2))

    print(f"\n{cat1} - {cat2}")
    print(f"Distance euclidienne moyenne : {np.mean(euclidian)}")
    print(f"Similarité cosinus moyenne : {np.mean(cosine)}")


    #TODO
    # - Regarder si distance est bonne ou pas
    # - S'intéresser à la longueur des vecteur
    # - Ecrire programme pour attribuer des catégorie aux relations