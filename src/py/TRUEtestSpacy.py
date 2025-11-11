import spacy as sp
from collections import defaultdict

f = open('txt/Fondation.txt', 'r', encoding="utf-8")
texte = f.read()
f.close()

nlp = sp.load("fr_core_news_lg")
# doc = nlp(texte)



#------------------------------EXPLAIN FINE TAGS---------------------------------



# tags_uniques = sorted(set([token.tag_ for token in doc]))

# print("List of encountered tags and their explanations:\n")
# for tag in tags_uniques:
#     explanation = sp.explain(tag)
#     if explanation is None:
#         explanation = "No explanation available (fine morphology: " + tag + ")"
#     print(f"{tag:25} -> {explanation}")



#------------------------------SENTENCE ANALYZER---------------------------------



# texte = '''Il cherche à récupérer son job, ou n’importe quelle autre place dans le Service. Pauvre gosse ! Il est désespéré ! Mais que voulais-tu que, moi, je lui dise ?... R. Sammy'''

# nlp = sp.load("fr_core_news_sm")
# doc = nlp(texte)
# for token in doc:
#     print(f"{token.text:<15}{token.lemma_:<15}{token.pos_:<10}{token.tag_:<10}{token.dep_:<10}{token.shape_:<10}{token.is_alpha:<10}{token.is_stop:<10}")



#------------------------------Test Modif build_entity_aliases---------------------------------



def build_entity_aliases1(entities_list):
    
    # Sort entities by length (longest first)
    sorted_entities = sorted(set([e.text for e in entities_list]), key=len, reverse=True)
    
    # Mapping dictionary: (alias, coordonate) -> canonical form
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
    return alias_map

def build_entity_aliases2(entities_list):
    
    # Sort entities by length (longest first)
    sorted_entities = sorted([e for e in entities_list], key=len, reverse=True)
    
    # Mapping dictionary: alias -> canonical form
    alias_map = {}
    
    # For each entity, check if it is a subset of another
    for entity in sorted_entities:
            
        # This entity becomes its own canonical form
        canonical = entity.text
        alias_map[(entity.text, entity.start)] = canonical
        
        # Extract words from the entity
        words = [token.text for token in entity]
        
        # If it's a compound name (2+ words), create aliases for the parts
        if len(words) >= 2:
            # Try the last word (usually surname)
            last_word = words[-1]
            if len(last_word) > 2:  # Avoid initials
                # Check if this short word already exists in our list
                if last_word != entity.text:
                    alias_map[(last_word, entity.end)] = canonical
            
            # Try the first word (first name)
            first_word = words[0]
            if len(first_word) > 2 and len(words) == 2:
                if first_word in sorted_entities and first_word != entity.text:
                    alias_map[(first_word.text, entity.start)] = canonical    
    return sorted(alias_map.items(), key=lambda x: x[0][1])

def mapping_entity(entities_list, alias_map):
    entity_map = {}
    for entity in entities_list:    # Pour chaque entité
        canonical = [alias_map[alias] for alias in alias_map.keys() if entity.text == alias]    #On cherche la forme cannonique
        if not canonical:   #Msg si on ne trouve pas d'alias relatif à l'entité
            print(f"Pb fct mapping_entity():\nAucun alias ne correspond à l'entité : {entity.text}")
        else:               #Sinon, on sauvegarde l'entité et sa coordonnée ainsi que sa forme cannonique
            entity_map[(entity.text, entity.start, entity.end)] = canonical
    return entity_map

def build_entity_relation(entity_map):
    relations_map = defaultdict(int)
    sorted_entities = sorted(entity_map.items(), key=lambda item: item[0][1])

    for i, entity in enumerate(sorted_entities):
        for neighbor in sorted_entities[i+1:]:
            if neighbor[0][2] - entity[0][2] > 25:  # Si la distance entre les entités aiccède 25 tokens
                break                               # On arrête la recherche de relation 
            if entity[1][0] != neighbor[1][0]:      # Éviter les auto-relations
                relations_map[(entity[1][0], neighbor[1][0])] += 1

    to_delete = []
    keys = list(relations_map.keys())
    for i, relation in enumerate(keys):
        for invert_relation in keys[i+1:]:
            if relation[0] == invert_relation[1] and relation[1] == invert_relation[0]: # Pour chaque doublon de relation
                relations_map[relation] += relations_map[invert_relation]   # On additionne leurs occurences
                to_delete.append(invert_relation)
                break

    for key in to_delete:   # On supprime les doublons
        del relations_map[key]

    return relations_map

# with open("./txt/les_cavernes_d_acier/chapter_1.txt", "r", encoding="utf-8") as f:
#         contenu = f.read()

contenu = "Emmanuel Macron est le président de la France. Il a rencontré Angela Merkel à Berlin. Ensuite, Macron a pris Merkel sur la table. Angela a bien aimé !"

doc = nlp(contenu)

LP=[]
for ent in doc.ents:           
    if ent.label_ == "PER":
        LP.append(ent)
alias_map = build_entity_aliases1(LP)
entity_map = mapping_entity(LP, alias_map)
print(LP)
print("\n\n----------------------\n\n")
print(alias_map)
print("\n\n----------------------\n\n")
print(entity_map)
print("\n\n----------------------\n\n")
print(build_entity_relation(entity_map))