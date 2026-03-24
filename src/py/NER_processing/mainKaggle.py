import os
import json
import re
from tqdm import tqdm 
import networkx as nx
import pandas as pd
import spacy as sp
from sentence_transformers import SentenceTransformer
from py.text_preprocessing.utils import clean_entity_name, filter_antidict
from py.NER_processing.utils import is_valid_entity, build_entity_aliases, mapping_entity, build_entity_relation, merge_entity_counts, mappingAliasesWithGraph, mappingAliasesWithGraphV2


#------------------------------ENTITY EXTRACTION-------------------------------

def _extract_num(fname):
    m = re.search(r'\d+', fname)
    return int(m.group()) if m else -1



params = {
    "minThreshold_textuel": 0,
    # "minThreshold_contextuel": 50,
    "minThreshold_final": 80,
    "weight_textuel": 0.4,
    "weight_contextuel": 0.6,
}

st = SentenceTransformer("dangvantuan/sentence-camembert-large")
nlp = sp.load("fr_core_news_lg")

anti_words = filter_antidict('fonctionnels_fr.txt')

books = [('paf', './txt/corpus_kaggle/prelude_a_fondation/modify'),
         ('lca', './txt/corpus_kaggle/les_cavernes_d_acier/modify')
        ]

df_dict = {"ID": [], "graphml": []}
entities_output = []  # List to store all extracted entities
PER_map = {}  # To store the final PER mapping

for code_book, filepath in books:

    files = [f for f in os.listdir(filepath) if f.endswith('.txt')] # Get all .txt files and sort by chapter number
    files_sorted = sorted(files, key=lambda x: _extract_num(x)) # Sort files by the number in the name
    for file in files_sorted:
        chemin_complet = os.path.join(filepath, file)
        num_chapter = _extract_num(file)-1
        if os.path.isfile(chemin_complet) and file.endswith('.txt'):
            f = open(chemin_complet, 'r', encoding="utf-8")
            corpus = f.read()
            f.close()

            doc = nlp(corpus)
            LP = []
            LM = []

            for ent in doc.ents:           
                if ent.label_ == "PER" and is_valid_entity(ent.text):
                    LP.append(ent)
                elif ent.label_ == "MISC":
                    LM.append(ent)

            # Build alias maps for each entity type
            alias_map_PER = mappingAliasesWithGraphV2(doc, st, LP, params) #build_entity_aliases(LP, entity_type="PER")
            PER_map = mapping_entity(LP, alias_map_PER)
            relations_PER = build_entity_relation(PER_map)
            alias_map_MISC = build_entity_aliases(LM, entity_type="MISC")

            # Merge counts using aliases
            LP_counts = merge_entity_counts(LP, alias_map_PER)
            LM_counts = merge_entity_counts(LM, alias_map_MISC)

            # Create a list of aliases used for this chapter (for traceability), en nettoyant les noms
            aliases_used = {
                "PER": {clean_entity_name(alias): clean_entity_name(canonical) for alias, canonical in alias_map_PER.items() 
                        if alias != canonical},
                "MISC": {clean_entity_name(alias): clean_entity_name(canonical) for alias, canonical in alias_map_MISC.items() 
                         if alias != canonical}
            }

            # Clean entities and prepare output structure
            chapter_entities = {
                "book_code": code_book,
                "file": file,
                "chapter_number": num_chapter,
                "entities": {
                    "PER": [{"name": clean_entity_name(name), "type": "PER", "count": count} 
                            for name, count in sorted(LP_counts.items())],
                    "MISC": [{"name": clean_entity_name(name), "type": "MISC", "count": count} 
                            for name, count in sorted(LM_counts.items())]
                },
                "aliases": aliases_used,  # Add aliases for transparency
                "summary": {
                    "total_persons": len(LP_counts),
                    "total_misc": len(LM_counts)
                }
            }

            entities_output.append(chapter_entities)

            # for ent in sorted(set(LP)):
            #     print(f"{ent:<30}{LP.count(ent)}")    #Prints found entities

            print(code_book, ", ", file, ", ", num_chapter)
            print("Number of detected characters : ", len(LP_counts))
            print("Number of uncategorized entities : ", len(LM_counts))
            
            # Display alias groupings
            if aliases_used["PER"]:
                print(f"  → {len(aliases_used['PER'])} PER aliases detected")
                
            print('\n ---------------------------\n')



#-------------------------------GRAPH CREATION--------------------------------



            G = nx.Graph()
            # Use canonical forms for graph nodes
            for canonical_name in LP_counts.keys():
                G.add_node(canonical_name)
                G.nodes[canonical_name]["names"] = canonical_name
            for key, value in relations_PER.items():
                G.add_edge(key[0], key[1], weight=value)

            df_dict["ID"].append("{}{}".format(code_book, num_chapter))
            graphml = "".join(nx.generate_graphml(G))
            df_dict["graphml"].append(graphml)



#------------------------------GRAPH EXPORT------------------------------



df = pd.DataFrame(df_dict)
df.set_index("ID", inplace=True)
df.to_csv("./EvanMASSOL_MartinGERIS.csv")

# Export named entities to a json file
with open("./json/entities_output.json", "w", encoding="utf-8") as json_file:
    json.dump(entities_output, json_file, ensure_ascii=False, indent=2)

# Create a comprehensive alias report
all_aliases = {"PER": {}, "MISC": {}}
for chapter in entities_output:
    for entity_type in ["PER", "MISC"]:
        all_aliases[entity_type].update(chapter["aliases"][entity_type])

# Export alias report to a json file
with open("./json/aliases_report.json", "w", encoding="utf-8") as json_file:
    json.dump(all_aliases, json_file, ensure_ascii=False, indent=2)

print("\nNamed entities exported to 'json/entities_output.json'")
print(f"Total chapters processed: {len(entities_output)}")
print(f"Alias report generated in 'json/aliases_report.json'")
print(f"  - {len(all_aliases['PER'])} PER aliases detected")
print(f"  - {len(all_aliases['MISC'])} MISC aliases detected")


print("\n -------------------- \n")
print(PER_map)