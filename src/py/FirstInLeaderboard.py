import spacy as sp
import networkx as nx
import pandas as pd
from unidecode import unidecode
import os
import re
import json
from collections import Counter

#-------------------------------------FUNCTIONS-------------------------------------



# Load the anti-dictionary
def filter_antidict(file):
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)
    
def is_valid_entity(text):
    """Strict filter to eliminate PDF extraction artifacts, including Unicode dashes"""
    text = text.strip()
    # List of Unicode dashes to filter
    unicode_dashes = "-–—―‒‑⁻−"
    # Eliminate entities that contain only numbers or non-alphabetic characters
    if not re.search(r'[a-zA-ZÀ-ÿ]', text):
        return False
    # Eliminate entities containing Unicode dashes
    if any(dash in text for dash in unicode_dashes):
        return False
    # Eliminate words with typical PDF break patterns
    if re.search(r"[a-z][A-Z]|[A-Z]{3,}|[a-z]{1,2}'[a-z]{1,2}", text):
        return False
    # Final validation: must resemble a proper name
    if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s]{2,}$', text):
        return False
    # Anti-dictionary filter
    if unidecode(text.lower()) in anti_words:
        return False
    return True


def build_entity_aliases(entities_list, entity_type="PER", manual_aliases_file="./json/manual_aliases.json"):
    """
    Builds a dictionary of aliases to group variants of the same entity.
    Automatically detects relationships between full names and short names.
    
    Args:
        entities_list: List of entities to process
        entity_type: Entity type ("PER", "LOC", "MISC")
        manual_aliases_file: Path to the manual aliases JSON file
    
    Returns: dict {alias -> canonical_form}
    """
    # Load manual aliases from the JSON file if it exists
    manual_aliases = {}
    if os.path.exists(manual_aliases_file):
        try:
            with open(manual_aliases_file, 'r', encoding='utf-8') as f:
                all_manual = json.load(f)
                manual_aliases = all_manual.get(entity_type, {})
        except Exception as e:
            print(f"Warning: unable to load {manual_aliases_file}: {e}")
    
    # Sort entities by length (longest first)
    sorted_entities = sorted(set([e.text for e in entities_list]), key=len, reverse=True)
    
    # Mapping dictionary: alias -> canonical form
    alias_map = {}
    
    # For each entity, check if it is a subset of another
    for entity in sorted_entities:
        # If already mapped, skip
        if entity in alias_map:
            continue
            
        # This entity becomes its own canonical form
        canonical = entity
        alias_map[entity] = canonical
        
        # Extract words from the entity
        words = entity.split()
        
        # If it's a compound name (2+ words), create aliases for the parts
        if len(words) >= 2:
            # Try the last word (usually surname)
            last_word = words[-1]
            if len(last_word) > 2:  # Avoid initials
                # Check if this short word already exists in our list
                if last_word in sorted_entities and last_word != entity:
                    alias_map[last_word] = canonical
            
            # Try the first word (first name)
            first_word = words[0]
            if len(first_word) > 2 and len(words) == 2:
                if first_word in sorted_entities and first_word != entity:
                    alias_map[first_word] = canonical
    
    # Add manual aliases (they take precedence and overwrite auto detections)
    alias_map.update(manual_aliases)
    
    return alias_map


def merge_entity_counts(entities_list, alias_map):
    """
    Merges entity counts using the alias map.
    
    Returns: Counter with grouped entities
    """
    merged_counts = Counter()
    
    for entity in entities_list:
        # Get the canonical form
        canonical = alias_map.get(entity.text, entity.text)
        merged_counts[canonical] += 1
    
    return merged_counts
    


#------------------------------ENTITY EXTRACTION-------------------------------



nlp = sp.load("fr_core_news_lg")

anti_words = filter_antidict('fonctionnels_fr.txt')

books = [('paf', './txt/prelude_a_fondation'),
         ('lca', './txt/les_cavernes_d_acier')
        ]

df_dict = {"ID": [], "graphml": []}
entities_output = []  # List to store all extracted entities

for code_book, filepath in books:
    files = [f for f in os.listdir(filepath) if f.endswith('.txt')] # Get all .txt files and sort by chapter number
    files_sorted = sorted(files, key=lambda x: int(re.search(r'\d+', x).group())) # Sort files by the number in the name
    for file in files_sorted:
        chemin_complet = os.path.join(filepath, file)
        num_chapter = int(re.search(r"\d+", file).group())-1
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
            alias_map_PER = build_entity_aliases(LP, entity_type="PER")
            alias_map_MISC = build_entity_aliases(LM, entity_type="MISC")

            # Merge counts using aliases
            LP_counts = merge_entity_counts(LP, alias_map_PER)
            LM_counts = merge_entity_counts(LM, alias_map_MISC)

            # Create a list of aliases used for this chapter (for traceability)
            aliases_used = {
                "PER": {alias: canonical for alias, canonical in alias_map_PER.items() 
                        if alias != canonical},
                "MISC": {alias: canonical for alias, canonical in alias_map_MISC.items() 
                         if alias != canonical}
            }

            # Create a dictionary for this chapter
            chapter_entities = {
                "book_code": code_book,
                "file": file,
                "chapter_number": num_chapter,
                "entities": {
                    "PER": [{"name": name, "type": "PER", "count": count} 
                            for name, count in sorted(LP_counts.items())],
                    "MISC": [{"name": name, "type": "MISC", "count": count} 
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


            # ADDITIONAL RELATIONSHIP EXTRACTION LOGIC HERE


            # TEXT PREPROCESSING



#-------------------------------GRAPH CREATION--------------------------------



            G = nx.Graph()
            # Use canonical forms for graph nodes
            for canonical_name in LP_counts.keys():
                G.add_node(canonical_name)
                G.nodes[canonical_name]["names"] = canonical_name

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