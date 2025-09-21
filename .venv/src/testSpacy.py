import spacy as sp
import fitz
import re
import os

# cwd = os.getcwd()
# print(cwd)
os.chdir('..')  #On remonte l'arborescence pour pouvoir atteindre les pdfs
os.chdir('..')
# cwd = os.getcwd()
# print(cwd)

def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
    return text

corpus = pdf_to_text("./Corpus/Corpus_ASIMOV/Fondation_sample.pdf")
corpus = re.sub(r'\s+', ' ', corpus)    #Remplace '/n', '/t', ' ' isolé comme groupé par un espace
                                        #ATTENTION : ENLEVER LES NUMEROS DE PAGE AU CORPUS

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
LL = []
for ent in doc.ents:            #Pour anti-dictionnaire : SE SERVIR DES LEMMES
    if ent.label_ == "PER":
        LP.append(ent.text)
    elif ent.label_ == "LOC":
        LL.append(ent.text)
        
for ent in set(LP):
    print(f"{ent:<30}{LP.count(ent)}")
print("Nombre de personnages détéctés : ", len(set(LP)))
print("\n------------------------------------------------------\n")
for ent in set(LL):
    print(f"{ent:<30}{LL.count(ent)}")
print("Nombre de lieux détéctés : ", len(set(LL)))

