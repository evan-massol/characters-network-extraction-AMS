import spacy as sp
from collections import defaultdict
import os

# f = open('txt/Fondation_sample.txt', 'r', encoding="utf-8")
# texte = f.read()
# f.close()

# nlp = sp.load("fr_core_news_lg")
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



# texte = ''' Salut, ça va ? Pour dire la vérité, répondit Evan, vous parlerez.'''

# nlp = sp.load("fr_core_news_lg")
# doc = nlp(texte)
# for token in doc:
#     print(f"{token.text:<15}{token.lemma_:<15}{token.pos_:<10}{token.tag_:<10}{token.dep_:<10}{token.shape_:<10}{token.is_alpha:<10}{token.is_stop:<10}")
# print("\n---------------------\n")
# for en in doc.ents:
#     print(f"{en.text} : {en.label_}")



#------------------------------TEXT'S CHAR ANALYZER--------------------------------



char = "- "
repertoire = './txt/corpus_kaggle/les_cavernes_d_acier/modify/'
for nom_fichier in os.listdir(repertoire):
    chemin_fichier = os.path.join(repertoire, nom_fichier)
    f = open(chemin_fichier, 'r', encoding="utf-8")
    corpus = f.read()
    f.close()
    pos = 0
    while True:
        pos = corpus.find(char, pos)
        if pos == -1:
            break
        print(corpus[max(0, pos-50): pos+50+len(char)])
        print("\n---------------------\n")
        pos += len(char)

print("###########################\n")
print("###########################\n")
print("###########################\n")

repertoire = './txt/corpus_kaggle/prelude_a_fondation/modify/'
for nom_fichier in os.listdir(repertoire):
    chemin_fichier = os.path.join(repertoire, nom_fichier)
    f = open(chemin_fichier, 'r', encoding="utf-8")
    corpus = f.read()
    f.close()
    pos = 0
    while True:
        pos = corpus.find(char, pos)
        if pos == -1:
            break
        print(corpus[max(0, pos-50): pos+50+len(char)])
        print("\n---------------------\n")
        pos += len(char)

# compteur_lca = {}
# repertoire = './txt/corpus_kaggle/les_cavernes_d_acier/modify/'
# for nom_fichier in os.listdir(repertoire):
#     chemin_fichier = os.path.join(repertoire, nom_fichier)
#     f = open(chemin_fichier, 'r', encoding="utf-8")
#     corpus = f.read()
#     f.close()
#     for caractere in corpus:
#         if caractere in compteur_lca:
#             compteur_lca[caractere] += 1
#         else:
#             compteur_lca[caractere] = 1

# for caractere, nombre in compteur_lca.items():
#     print(f"'{caractere}' : {nombre}")

# print("\n---------------------\n")

# compteur_paf = {}
# repertoire = './txt/corpus_kaggle/prelude_a_fondation/modify/'
# for nom_fichier in os.listdir(repertoire):
#     chemin_fichier = os.path.join(repertoire, nom_fichier)
#     f = open(chemin_fichier, 'r', encoding="utf-8")
#     corpus = f.read()
#     f.close()
#     for caractere in corpus:
#         if caractere in compteur_paf:
#             compteur_paf[caractere] += 1
#         else:
#             compteur_paf[caractere] = 1

# for caractere, nombre in compteur_paf.items():
#     print(f"'{caractere}' : {nombre}")



#------------------------------SPACY'S MISCS ANALYSE-----------------------------



# nlp = sp.load("fr_core_news_sm")
# repertoire = './txt/corpus_kaggle/les_cavernes_d_acier/modify'

# for nom_fichier in os.listdir(repertoire):
#     chemin_fichier = os.path.join(repertoire, nom_fichier)
#     f = open(chemin_fichier, 'r', encoding="utf-8")
#     corpus = f.read()
#     f.close()

#     doc = nlp(corpus)
#     LM = []
#     for ent in doc.ents:
#         if ent.label_ == "MISC":
#             LM.append(ent)
#             phrase = ent.sent.text
#             print(f"{ent.text} : {phrase}")
#             print("\n---------------------\n")

# print("\n\n---------------------\n")
# print("---------------------\n")
# print("---------------------\n\n")

# nlp = sp.load("fr_core_news_sm")
# repertoire = './txt/corpus_kaggle/prelude_a_fondation/modify'

# for nom_fichier in os.listdir(repertoire):
#     chemin_fichier = os.path.join(repertoire, nom_fichier)
#     f = open(chemin_fichier, 'r', encoding="utf-8")
#     corpus = f.read()
#     f.close()

#     doc = nlp(corpus)
#     LM = []
#     for ent in doc.ents:
#         if ent.label_ == "MISC":
#             LM.append(ent)
#             phrase = ent.sent.text
#             print(f"{ent.text} : {phrase}")
#             print("\n---------------------\n")



#-------------------------------SPACY'S EN ANALYSE-------------------------------



# nlp = sp.load("fr_core_news_lg")
# repertoire = './txt/corpus_kaggle/les_cavernes_d_acier/modify'
# LM = []
# LP = []

# for nom_fichier in os.listdir(repertoire):
#     chemin_fichier = os.path.join(repertoire, nom_fichier)
#     f = open(chemin_fichier, 'r', encoding="utf-8")
#     corpus = f.read()
#     f.close()

#     doc = nlp(corpus)
#     for ent in doc.ents:
#         if ent.label_ == "MISC":
#             LM.append(ent)
#         if ent.label_ == "PER":
#             LP.append(ent)
    
# print("PER : ", len(LP))
# print("MISC : ", len(LM))

