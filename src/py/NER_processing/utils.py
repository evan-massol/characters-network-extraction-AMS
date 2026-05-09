import os
import re
import json
from unidecode import unidecode
from itertools import combinations
import numpy as np
from rapidfuzz import fuzz
from collections import Counter, defaultdict
import networkx as nx
import spacy as sp
from tqdm import tqdm 
from py.text_preprocessing.utils import ANTI_DICT

###FUNCTIONS

def is_valid_entity(text : str) -> bool:
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
    # Final validation: must resemble a proper noun
    if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s]{2,}$', text):
        return False
    # Anti-dictionary filter
    if unidecode(text.lower()) in ANTI_DICT:
        return False
    return True

def _normalize_manual_aliases(raw_aliases):
    """Normalize manual alias definitions to the alias->canonical mapping."""
    normalized = {}
    for key, value in raw_aliases.items():
        if isinstance(value, list):
            canonical = key
            # Ensure canonical name maps to itself for downstream lookups
            normalized.setdefault(canonical, canonical)
            for alias in value:
                normalized[alias] = canonical
        else:
            normalized[key] = value
    return normalized


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
                manual_aliases = _normalize_manual_aliases(all_manual.get(entity_type, {}))
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


def mapping_entity(entities_list, alias_map):
    '''
    Build a map to link each occurrence of an entity named to its cannocical form. Load its 
    start and end index in the token list.
    Args:
        entities_list (List) : 
            Entities detected by the NER model.
        alias_map (Map) : 


    Returns:
        Map [(entityNamed_text, tokenNum_start, tokenNum_end):canonical_form] : 
            Map which link each entity named detected to its canonical form.
    '''
    entity_map = {}
    for entity in entities_list:    # Pour chaque entité
        canonical = [alias_map[alias] for alias in alias_map.keys() if entity.text == alias]    #On cherche la forme cannonique
        canonical = canonical[0]
        if not canonical:   #Msg si on ne trouve pas d'alias relatif à l'entité
            print(f"Pb fct mapping_entity():\nAucun alias ne correspond à l'entité : {entity.text}")
        else:               #Sinon, on sauvegarde l'entité et ses coordonnées ainsi que sa forme cannonique
            entity_map[(entity.text, entity.start, entity.end)] = canonical
    return entity_map
    
def build_entity_relation(entity_map):
    '''
    Build a map to load the occurences of each relation between two entities.
    Args:
        entity_map (Map) : 
            Map [(entityNamed_text, tokenNum_start, tokenNum_end):canonical_form] which link 
            each entity named detected to its canonical form.
    Returns:
        Map [(entityNamed_1, entityNamed_2):occurences_number] : 
            Map which link each couple of entities named detected to their number of occurences.
    '''
    relations_map = defaultdict(int)
    sorted_entities = sorted(entity_map.items(), key=lambda item: item[0][1])

    for i, entity in enumerate(sorted_entities):
        for neighbor in sorted_entities[i+1:]:
            if neighbor[0][1] - entity[0][2] > 25:  # Si la distance entre les entités excède 25 tokens
                break                               # On arrête la recherche de relation pour cette entité
            if entity[1] != neighbor[1]:      # Éviter les auto-relations
                relations_map[(entity[1], neighbor[1])] += 1

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


# ------------------------------------------------------------------------------ S2 METHOD

def receiveSentence(text: str, start: int, end: int) -> str:
    """
    Detect the start and the end of sentences on based of boundaries.
    
    Args:
      doc: Original string where detected entities
      start: Index of the first boundary
      end: Index of the last boundary
    
    Returns: String
    """
    sentence_separators = ".!?"

    left = start
    while left > 0 and text[left] not in sentence_separators:
        left -= 1
    if left != 0:
        left += 1

    right = end
    while right < len(text) and text[right] not in sentence_separators:
        right += 1
    if right < len(text):
        right += 1

    return text[left:right].strip()

def receiveSentenceTokenized(doc, start, end):
    """
    Detect the start and the end of sentences on based of boundaries.
    Use token of SpaCy.
    
    Args:
      doc: Original Span build by SpaCy
      start: Index of the first boundary
      end: Index of the last boundary
    
    Returns: Span
    """
    sentence_separators = {".", "!", "?"}

    left = start
    while left > 0 and doc[left].text not in sentence_separators:
        left -= 1
    if left != 0:
        left += 1

    right = end
    while right < len(doc) and doc[right].text not in sentence_separators:
        right += 1
    if right < len(doc):
        right += 1
    
    return doc[left:right]

def embeddedMainTokens(sentence, model):
    """
    Collect meaningful words in a sentence. Use token of SpaCy. 
    Then, embedded these words and calcul their average.
    
    Args:
      sentence: Span of SpaCy
      model: Sentence transformer model
    
    Returns: Vector ?
    """
    main_words=[]
    for word in sentence:
        if word.pos_ in ["ADJ", "VERB", "NOUN"]:
            main_words.append(word.text)
    if not main_words:
        print("RENVOIE NUL")
        return None
        
    embeddings = model.encode(main_words)
        
    return np.mean(embeddings, axis=0)  # On peut aussi remplacer mean par sum mais ca a pas l'air aussi puissant

def mappingAliasesWithGraph(text, model, entities_list, params):
    """
    Builds a dictionary of aliases to group variants of the same entity.
    Start by creating an alias graph. The links are calculated based on 
    textual and contextual similarity. The contextual similarity is based
    on the entities' sentences Use a Louvin clustering algorithm to detect 
    clusters of aliases.
    
    Args:
      text: Original string where detected entities
      model: sentence transformer model
      entities_list: List of entities to process
      params: Maps of weights and thresholds
    
    Returns: dict {alias -> canonical_form}
    """
    G = nx.Graph()
    entities_map = {}

    p_mtt = params["minThreshold_textuel"]
    p_wt = params["weight_textuel"]
    p_wc = params["weight_contextuel"]
    p_mtf = params["minThreshold_final"]

    for ent in tqdm(entities_list, desc="Embedding des Aliases"):
        id = ent.start
        G.add_node(
            id,
            span=ent,
            embedding=model.encode(receiveSentence(text, ent.start_char, ent.end_char))
        )

    for n1, n2 in tqdm(combinations(G.nodes, 2), desc="Comparaisons des Aliases"):

        ent1 = G.nodes[n1]["span"]
        ent2 = G.nodes[n2]["span"]

        # CALCUL CONTEXTUEL RATIO
        emb1 = G.nodes[n1]["embedding"]
        emb2 = G.nodes[n2]["embedding"]
        contextuel_ratio = model.similarity(emb1, emb2).item()*100
        contextuel_ratio = round(contextuel_ratio, 3)
        
        # CALCUL TEXTUEL RATIO
        textuel_ratio = fuzz.partial_token_set_ratio(ent1.text, ent2.text)
        textuel_ratio = round(textuel_ratio, 3)

        # CALCUL FINAL RATIO

        final_ratio = p_wt*textuel_ratio + p_wc*contextuel_ratio

        if (final_ratio>=p_mtf):
            G.add_edge(n1, n2, weight=final_ratio)

    entities_communities = nx.community.louvain_communities(G, seed=42) #On identifie les clusters

    for community in entities_communities:
        entities = [G.nodes[n]["span"].text for n in community]
        entities = list(set(entities))
        canonical = max(entities, key=len)
        for entity in entities:
            entities_map[entity] = canonical

    return entities_map

def mappingAliasesWithGraphV2(doc, model, entities_list, params):
    """
    Builds a dictionary of aliases to group variants of the same entity.
    Start by creating an alias graph. The links are calculated based on 
    textual and contextual similarity. Contextual similarity is based on 
    the meaningful words in the entities' sentences. Use a Louvin 
    clustering algorithm to detect clusters of aliases.
    
    Args:
      text: Original string where detected entities
      model: sentence transformer model
      entities_list: List of entities to process
      params: Maps of weights and thresholds
    
    Returns: dict {alias -> canonical_form}
    """
    G = nx.Graph()
    entities_map = {}
    p_mtt = params["minThreshold_textuel"]
    p_wt = params["weight_textuel"]
    p_wc = params["weight_contextuel"]
    p_mtf = params["minThreshold_final"]
    p_mtc = params["minThreshold_contextuel"]
    p_lr = params["louvain_resolution"]

    for ent in tqdm(entities_list, desc="Embedding des Aliases"):
        id = ent.start
        G.add_node(
            id, 
            span=ent,
            embedding=embeddedMainTokens(receiveSentenceTokenized(doc, ent.start, ent.end), model)
        )

    for n1, n2 in tqdm(combinations(G.nodes, 2), desc="Comparaisons des Aliases"):

        ent1 = G.nodes[n1]["span"]
        ent2 = G.nodes[n2]["span"]

        # CALCUL CONTEXTUEL RATIO
        emb1 = G.nodes[n1]["embedding"]
        emb2 = G.nodes[n2]["embedding"]
        isEmbeddings = emb1 is not None and emb2 is not None

        contextuel_ratio = 100
        if isEmbeddings:
            contextuel_ratio = model.similarity(emb1, emb2).item()*100
            contextuel_ratio = round(contextuel_ratio, 3)

        # CALCUL TEXTUEL RATIO
        textuel_ratio = fuzz.partial_token_set_ratio(ent1.text, ent2.text)
        textuel_ratio = round(textuel_ratio, 3)

        if (textuel_ratio >= p_mtt and contextuel_ratio >= p_mtc):

            # CALCUL FINAL RATIO

            if (isEmbeddings):
                final_ratio = p_wt*textuel_ratio + p_wc*contextuel_ratio
            else:
                final_ratio=textuel_ratio

            if (final_ratio>=p_mtf):
                G.add_edge(n1, n2, weight=final_ratio)

    entities_communities = nx.community.louvain_communities(G, resolution=p_lr, seed=42)

    for community in entities_communities:
        entities = [G.nodes[n]["span"].text for n in community]
        entities = list(set(entities))
        canonical = max(entities, key=len)
        for entity in entities:
            entities_map[entity] = canonical

    return entities_map

def build_entity_relation_with_context(doc, model, entity_map):
    '''
    Build a map to load different contextual sentences of each relation between two entities.
    Args:
        entity_map (Map) : 
            Map [(entityNamed_text, tokenNum_start, tokenNum_end):canonical_form] which link 
            each entity named detected to its canonical form.
    Returns:
        Map [(entityNamed_1, entityNamed_2):sentences_list] : 
            Map which link each couple of entities named detected to their contextual sentences.
    '''
    relations_map = defaultdict(list)
    sorted_entities = sorted(entity_map.items(), key=lambda item: item[0][1]) # On tri par l'indexe de début de l'entité

    for i, entity in tqdm(enumerate(sorted_entities), desc="Embedding des contexts de relation"):
        for neighbor in sorted_entities[i+1:]:
            if neighbor[0][1] - entity[0][2] > 25:  # Si la distance entre les entités excède 25 tokens
                break                               # On arrête la recherche de relation pour cette entité
            if entity[1] != neighbor[1]:      # Éviter les auto-relations
                context = receiveSentenceTokenized(doc, entity[0][1], neighbor[0][2]) #Extraction du context (phrase de la première entité + de la dernière + celle entre les deux entités)
                embedded_context = embeddedMainTokens(context, model)
                relations_map[(entity[1], neighbor[1])].append(embedded_context)
    return relations_map