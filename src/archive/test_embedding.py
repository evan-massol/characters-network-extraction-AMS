from sentence_transformers import SentenceTransformer
from itertools import combinations

phrases = [
    # "Il y a un temps magnifique",
    # "Il fait beau aujourd'hui",
    "Il pleut toute la semaine.",
    "Il a neigé hier. Apparemment, le temps se gâte.",
    "Il y avait de la neige.",
    "Il a neigé hier.",
    # "Paris est la capitale de la France"
]

model = SentenceTransformer("dangvantuan/sentence-camembert-large")

for s1, s2 in combinations(phrases, 2):
    emb1 = model.encode(s1)
    emb2 = model.encode(s2)
    print("\n#########################\n")
    print(s1)
    print("-------------------------")
    print(s2)
    print("-------------------------")
    print(model.similarity(emb1, emb2).item()*100)