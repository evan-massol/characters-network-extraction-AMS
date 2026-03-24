import os
from collections import Counter

import networkx as nx
import pandas as pd

import spacy as sp
from sentence_transformers import SentenceTransformer

from py.NER_processing.utils import is_valid_entity, build_entity_aliases, mapping_entity, build_entity_relation_with_context, merge_entity_counts


###############################################################################
# PLAN REWORK FOR THIS PROGRAM
#
# PIPELINE :
# for each corpus
#     - NER 
#     - handle alias 
#     - find relation 
#     - generate CSV with characters (their aliases) and relations (embeddings' meaningful words)
#
# In another program, we embedd contextual sentences
###############################################################################



#--------------------------------INITIALISATION--------------------------------



repertoire = './txt/corpus_classique/'
df_dict = {"ID": [], "graphml": []}

params = {
    "minThreshold_textuel": 0,
    "minThreshold_contextuel": 0,
    "minThreshold_final": 80,
    "weight_textuel": 0.4,
    "weight_contextuel": 0.6,
    "louvain_resolution": 0.8
}

st = SentenceTransformer("dangvantuan/sentence-camembert-large")
nlp = sp.load("fr_core_news_lg")



#------------------------------TEXTS PROCESSING---------------------------------



for file in os.listdir(repertoire):
    if file.endswith(".txt"):

        print(f"Processing {file}...")

        path = os.path.join(repertoire, file)
        f = open(path, 'r', encoding="utf-8")
        corpus = f.read()
        f.close()


        doc = nlp(corpus)

        LP = []
        for ent in doc.ents:
            if ent.label_ == "PER" and is_valid_entity(ent.text):
                LP.append(ent)

        # Aliases handling
        alias_map_PER = build_entity_aliases(LP, entity_type="PER")
        PER_map = mapping_entity(LP, alias_map_PER)


        #########################
        # LA SUITE EST A MODIFIER
        #########################

        # Relation handling
        relations_PER = build_entity_relation_with_context(PER_map) #LA FONCTION N'EST PAS FINI

        # Merge counts using aliases
        LP_counts = merge_entity_counts(LP, alias_map_PER)

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