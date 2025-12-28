import fitz
import os
import re
import json
from unidecode import unidecode
from collections import Counter, defaultdict

###FUNCTIONS


def filter_antidict(file : str) -> set:
    """Load anti-dictionary words from a file."""
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)


def pdf_to_text(pdf_path : str) -> str:
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

def clean_entity_name(name : str | list) -> str:
    """Remove unwanted newlines and extra spaces from entity names."""
    if isinstance(name, list):
        val = ' '.join(str(name) for name in name)
        return val
    return ' '.join(name.replace('\n', ' ').split())


# Remove incomplete sentences
def supprCutSentences(texte : str) -> str:
    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):             #Start from the end to avoid disrupting indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        last_ponct = max(avant.rfind('.'), avant.rfind('!'), avant.rfind('?'))
        if last_ponct != -1:
            avant = avant[:last_ponct+1]        #Remove after the last punctuation
        else:
            avant = ""

        texte = avant + " -_ENDPAGE_- " + apres #Keep markers to process post-marker sentences

    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):                       #Start from the beginning to avoid disrupting indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        if len(apres)!=0:
            premiere_lettre = next((c for c in apres if c.isalpha()))
            if not premiere_lettre.isupper():              #If no uppercase letter right after the marker
                apres_poncts = [apres.find('.'), apres.find('!'), apres.find('?')]
                if not all(x == -1 for x in apres_poncts):
                    apres_poncts = [x for x in apres_poncts if x != -1]
                first_ponct = min(apres_poncts)
                if first_ponct != -1:
                    apres = apres[first_ponct+1:]   #Remove before the first punctuation
                else:
                    apres = ""

        texte = avant + apres

    return texte

# Remove part titles
def supprPartsTitle(texte : str) -> str:
    texte = re.sub(r'\n[A-ZÈ]+ PART \n \n \n[A-ZÀÂÇÉÈÊËÎÏÔÙÛ ]+', '', texte)
    return texte

# Remove chapter numbers
def supprChapterNum(texte : str) -> str:
    texte = re.sub(r'\n\b[IVXLCDM]+(?!\')\b \n', '', texte)
    return texte

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


def mapping_entity(entities_list, alias_map):
    '''
    Returns a set (entityNamed_text, tokenNum_start, tokenNum_end):canonical_form
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
    Returns a set (entityNamed_1, entityNamed_2):occurences_number
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


###CONSTANTS
ANTI_DICT = filter_antidict('fonctionnels_fr.txt')

