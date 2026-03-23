# NOTE :
# L'algorithme peut avoir des performances varaibles en fonction de :
#   - L'algorithme de calcul de différence textuelle : ratio, partial_ratio, partial_token_set_ratio


import spacy as sp
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer



#########################
#         CODE
#########################

def receiveSentence(text: str, start: int, end: int) -> str:

    sentence_separators = ".!?"

    # Chercher le début de la phrase
    left = start
    while left > 0 and text[left] not in sentence_separators:
        left -= 1
    if left != 0:
        left += 1

    # Chercher la fin de la phrase
    right = end
    while right < len(text) and text[right] not in sentence_separators:
        right += 1
    if right < len(text):
        right += 1

    return text[left:right].strip()

f = open('txt/corpus_classique/Fondation_sample.txt', 'r', encoding="utf-8")
text = f.read()
f.close()

# text="Dans la ville de Riverton, la tension montait. Alexander Drake, ou simplement Alex, était déjà sur le pont, observant la rivière. Certains l'appelaient aussi le Stratège, à cause de ses plans toujours impeccables. Non loin de là, Beatrice Lemoine, connue sous le surnom de Bea, préparait une potion dans son laboratoire. Ses amis intimes l'appelaient parfois la Chimiste, tandis que les moins proches murmuraient la Sorcière de Riverton lorsqu'ils passaient près de chez elle. Pendant ce temps, Charles Monroe ou “Charlie” traînait dans les ruelles, évitant les gardes. Ses anciens compagnons de voyage le surnommaient Le Faucon, pour son habileté à disparaître en un clin d'œil, ou encore Monsieur M., quand il voulait rester discret. Dans le quartier général de la milice, Diana Velasquez, dite Di, supervisait les patrouilles. On la connaissait également sous le nom de l'Oeil de Riverton, en raison de sa vigilance inégalée, et certains soldats l'appelaient D.V., avec un respect mêlé de crainte. Enfin, dans les tavernes de la ville, Edward Chen ou “Eddie” racontait ses aventures. Ses surnoms étaient nombreux : le Voyageur, pour ses récits de contrées lointaines, ou E.C., lorsqu'il voulait garder l'anonymat."
personnages = {
    "Alexander Drake" : ["Alexander Drake", "Alex", "Stratège"],
    "Beatrice Lemoine" : ["Bea", "Chimiste", "Sorcière de Riverton"],
    "Charles Monroe" : ["Charlie", "Le Faucon", "Monsieur M."],
    "Diana Velasquez" : ["Di", "Oeil de Riverton", "D.V."],
    "Edward Chen" : ["Eddie", "Voyageur", "E.C."]
}

resultat = {}

st = SentenceTransformer("dangvantuan/sentence-camembert-large")
nlp = sp.load("fr_core_news_lg")

doc = nlp(text)
LP = []
LM = []

for ent in doc.ents:           
    if ent.label_ == "PER" :
        LP.append(ent)
    elif ent.label_ == "MISC":
        LM.append(ent)



G = nx.Graph()

for ent in LP:
    id = ent.start
    G.add_node(id, span=ent)
    # print(ent.text, "(", ent.start_char, ", ", ent.end_char, ") : ", receiveSentence(text, ent.start_char, ent.end_char))

for n1, n2 in combinations(G.nodes, 2):

    ent1 = G.nodes[n1]["span"]
    ent2 = G.nodes[n2]["span"]

    # CALCUL CONTEXTUEL RATIO

    s1 = receiveSentence(text, ent1.start_char, ent1.end_char)
    s2 = receiveSentence(text, ent2.start_char, ent2.end_char)
    emb1 = st.encode(s1)
    emb2 = st.encode(s2)
    contextuel_ratio = st.similarity(emb1, emb2).item()*100
    contextuel_ratio = round(contextuel_ratio, 3)

    # CALCUL TEXTUEL RATIO

    textuel_ratio = fuzz.partial_token_set_ratio(ent1.text, ent2.text)
    textuel_ratio = round(textuel_ratio, 3)

    # CALCUL FINAL RATIO

    final_ration = 0.5*textuel_ratio + 0.5*contextuel_ratio

    print(ent1.text, " - ", ent2.text, " : ", final_ration)
    if (textuel_ratio>=80):
        G.add_edge(n1, n2, weight=textuel_ratio)

entities_communities = nx.community.louvain_communities(G, seed=42)

for community in entities_communities:
    texts = [G.nodes[n]["span"].text for n in community]
    unique_texts = list(set(texts))
    key = max(unique_texts, key=len)
    resultat[key] = unique_texts




#########################
#     AFFICHAGE
#########################

print("Nb entity", len(LP))

print("SOLUTION : ")
for k, v in personnages.items():
    print(f"   {k} : {v}")
print("RESULTAT : ")
for k, v in resultat.items():
    print(f"   {k} : {v}")



labels = {n: G.nodes[n]["span"].text for n in G.nodes}
plt.figure(figsize=(8, 6))

# Dessiner le graphe
nx.draw(
    G,
    with_labels=True,      # afficher les labels
    labels=labels,         # utiliser le texte des entités comme label
    node_color='skyblue',
    node_size=2000,
    font_size=8,
    font_weight='bold',
    edge_color='gray'
)

plt.show()