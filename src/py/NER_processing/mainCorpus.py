import spacy as sp
import networkx as nx
import pandas as pd
from collections import Counter
from py.NER_processing.utils import is_valid_entity, build_entity_aliases, mapping_entity, build_entity_relation, merge_entity_counts


#------------------------------TEXT PROCESSING---------------------------------



f = open('txt/corpus_classique/Fondation_sample.txt', 'r', encoding="utf-8")
corpus = f.read()
f.close()

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
LM = []
df_dict = {"ID": [], "graphml": []}

for ent in doc.ents:
    if ent.label_ == "PER" and is_valid_entity(ent.text):
        LP.append(ent)
    elif ent.label_ == "MISC":
        LM.append(ent)

LP_text = Counter(ent.text for ent in LP)
LM_text = Counter(ent.text for ent in LM)

for text, count in sorted(LP_text.items()):
    print(f"{text:<30}{count}")
print("\n------------------------------------------------------\n")
for text, count in sorted(LM_text.items()):
    print(f"{text:<30}{count}")
print("\n------------------------------------------------------\n")
print("Number of detected characters: ", len(set(LP)))
print("Number of uncategorized entities: ", len(set(LM)))



# Build maps PER
alias_map_PER = build_entity_aliases(LP, entity_type="PER")
PER_map = mapping_entity(LP, alias_map_PER)
relations_PER = build_entity_relation(PER_map)

# Build maps MISC
alias_map_MISC = build_entity_aliases(LM, entity_type="MISC")

# Merge counts using aliases
LP_counts = merge_entity_counts(LP, alias_map_PER)
LM_counts = merge_entity_counts(LM, alias_map_MISC)

G = nx.Graph()
# Use canonical forms for graph nodes
for canonical_name in LP_counts.keys():
    G.add_node(canonical_name)
    G.nodes[canonical_name]["names"] = canonical_name
for key, value in relations_PER.items():
    G.add_edge(key[0], key[1], weight=value)

df_dict["ID"].append("Fondation")
graphml = "".join(nx.generate_graphml(G))
df_dict["graphml"].append(graphml)

df = pd.DataFrame(df_dict)
df.set_index("ID", inplace=True)
df.to_csv("./EvanMASSOL_MartinGERIS_Fondation.csv")