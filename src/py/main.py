import spacy as sp
import re
from unidecode import unidecode
from utils import is_valid_entity


#------------------------------TEXT PROCESSING---------------------------------



f = open('txt/Fondation.txt', 'r', encoding="utf-8")
corpus = f.read()
f.close()

nlp = sp.load("fr_core_news_md")
doc = nlp(corpus)

LP = []
LL = []
LM = []


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

