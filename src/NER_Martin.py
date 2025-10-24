import re
import spacy as sp
from unidecode import unidecode



#------------------------------INITIALISATION---------------------------------



#Création de la liste anti-dictionnaire
anti_words = []
f = open('fonctionnels_fr.txt', 'r', encoding="utf-8")
for line in f:
    anti_words.append(line.strip())
f.close()   

#Importation du texte
f = open('txt/Fondation.txt', 'r', encoding="utf-8")
corpus = f.read()
f.close()

L = []
LP = []
LL = []

nlp = sp.load("fr_core_news_sm", disable=[ "parser",
                                           '''"ner"''', 
                                           '''"lemmatizer"'''])
doc = nlp(corpus)



#------------------------------CONSTRUCTION L---------------------------------



sizeMax_EN = 5

# Ajout de toute potentielle entité nommée
tag_EN = ["NOUN", "PROPN", "ADJ", "DET"]
i=0
while i<len(doc):
    for taille in range(sizeMax_EN, 0 ,-1):
        window = doc[i:i+taille]
        if all(word.pos_ in tag_EN for word in window):
            L.append(window)
            i += taille
            break
        if taille == 1:
            i += 1

# Suppresions des tokens isolés indésirables
tagsFilter = ["NOUN", "ADJ", "DET"]
liste = []
for span in L:
    if (span.start!=span.end-1) or (span.start==span.end-1 and doc[span.start].pos_ not in tagsFilter):
        liste.append(span)
L = liste

# Suppression des doublons
L_unique = []
texte_vu = set()
for span in L:
    if span.text not in texte_vu:
        L_unique.append(span)
        texte_vu.add(span.text)
L = L_unique



#-----------------------------CONSTRUCTION LP---------------------------------



for span in L:
    # if any(word.text[0].isupper() for word in span):
    #     LP.append(span)
    if any(word.pos_ == "PROPN" for word in span):
        LP.append(span)

LP.sort(key=lambda span: (span.text))
for span in LP:
    print(f"{span.text:<30}{span.end - span.start} {span.label_}")
print(f"{len(L):<10}{len(LP):<10}{len(LL):<10}")