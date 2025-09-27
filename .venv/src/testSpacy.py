import spacy as sp
import fitz
import re
from unidecode import unidecode

def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

corpus = pdf_to_text("pdf/Fondation_sample.pdf")
corpus = re.sub(r'\s+', ' ', corpus)    #Remplace '/n', '/t', ' ' isolé comme groupé par un espace

# Charger l'antidictionnaire
def filter_antidict(file):
    with open(file, 'r', encoding='utf-8') as f:
        return set(unidecode(line.strip()) for line in f)

anti_words = filter_antidict('fonctionnels_fr.txt')

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
LL = []
LM = []
def is_valid_entity(text):
    """Filtre strict pour éliminer les artefacts d'extraction PDF, y compris les tirets Unicode"""
    text = text.strip()
    # Liste des tirets Unicode à filtrer
    tirets_unicode = "-–—―‒‑⁻−"
    # Éliminer les entités qui ne contiennent que des chiffres ou des caractères non-alphabétiques
    if not re.search(r'[a-zA-ZÀ-ÿ]', text):
        return False
    # Éliminer les entités contenant des tirets Unicode
    if any(tiret in text for tiret in tirets_unicode):
        return False
    # Éliminer les mots avec des patterns de coupure typiques des PDFs
    if re.search(r"[a-z][A-Z]|[A-Z]{3,}|[a-z]{1,2}'[a-z]{1,2}", text):
        return False
    # Validation finale: doit ressembler à un nom propre
    if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s]{2,}$', text):
        return False
    # Filtre anti-dictionnaire
    if unidecode(text.lower()) in anti_words:
        return False
    return True

for ent in doc.ents:            #Pour anti-dictionnaire : SE SERVIR DES LEMMES
    if ent.label_ == "PER" and is_valid_entity(ent.text):
        LP.append(ent.text)
    elif ent.label_ == "LOC" and is_valid_entity(ent.text):
        LL.append(ent.text)
    elif ent.label_ == "MISC":
        LM.append(ent.text)

for ent in sorted(set(LP)):
    print(f"{ent:<30}{LP.count(ent)}")
print("Nombre de personnages détéctés : ", len(set(LP)))
print("\n------------------------------------------------------\n")
for ent in sorted(set(LL)):
    print(f"{ent:<30}{LL.count(ent)}")
print("Nombre de lieux détéctés : ", len(set(LL)))
print("\n------------------------------------------------------\n")
for ent in set(LM):
    print(f"{ent:<30}{LM.count(ent)}")
print("Nombre d'entités non catégorisés : ", len(set(LM)))

