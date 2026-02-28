import re
from py.text_preprocessing.utils import pdf_to_text, supprPartsTitle, supprChapterNum, supprCutSentences

#-----------------------------PRETRAITEMENT DU TEXTE-------------------------------



corpus = pdf_to_text("./pdf/Fondation_sample.pdf") 
corpus = re.sub(r'\ufffd\s*\d+\s*\ufffd', ' ', corpus)  #Supprime les numéros de pages
corpus = supprPartsTitle(corpus)                        #Supprime les titres
corpus = supprChapterNum(corpus)                        #Supprime les numéros de chapitres
corpus = supprCutSentences(corpus)                      #Supprime les phrases coupées
corpus = re.sub(r'\s+', ' ', corpus)                    #Remplace '/n', '/t', ' ' isolé comme groupé par un espace



#-----------------------------------ECRITURE---------------------------------------



f = open('./txt/corpus_classique/Fondation_sample.txt', 'w', encoding="utf-8")
f.write(corpus)
f.close()