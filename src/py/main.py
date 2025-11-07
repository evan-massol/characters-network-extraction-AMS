import spacy as sp
import re
from unidecode import unidecode
from utils import filter_antidict


#------------------------------TEXT PROCESSING---------------------------------



f = open('txt/Fondation.txt', 'r', encoding="utf-8")
corpus = f.read()
f.close()
anti_words = filter_antidict('fonctionnels_fr.txt')

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
LL = []
LM = []
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
    # Final validation: must resemble a proper noun
    if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s]{2,}$', text):
        return False
    # Anti-dictionary filter
    if unidecode(text.lower()) in anti_words:
        return False
    return True

for ent in doc.ents:            #For anti-dictionary: USE LEMMAS
    if ent.label_ == "PER" and is_valid_entity(ent.text):
        LP.append(ent.text)
    elif ent.label_ == "LOC" and is_valid_entity(ent.text):
        LL.append(ent.text)
    elif ent.label_ == "MISC":
        LM.append(ent.text)

for ent in sorted(set(LP)):
    print(f"{ent:<30}{LP.count(ent)}")
print("\n------------------------------------------------------\n")
for ent in sorted(set(LL)):
    print(f"{ent:<30}{LL.count(ent)}")
print("\n------------------------------------------------------\n")
for ent in set(LM):
    print(f"{ent:<30}{LM.count(ent)}")
print("Number of detected characters: ", len(set(LP)))
print("Number of detected locations: ", len(set(LL)))
print("Number of uncategorized entities: ", len(set(LM)))

