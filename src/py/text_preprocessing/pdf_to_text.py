import re
import os
from py.text_preprocessing.utils import pdf_to_text, supprPartsTitle, supprChapterNum, supprCutSentences, removeChar, supprPageNum

#-----------------------------PRETRAITEMENT DU TEXTE-------------------------------


for pdf in os.listdir("./pdf/"):
    if pdf.endswith(".pdf"):
        print(f"Processing {pdf}...")
        corpus = pdf_to_text(os.path.join("./pdf/", pdf)) 
        corpus = supprPageNum( corpus)                          #Supprime les numéros de pages
        corpus = supprPartsTitle(corpus)                        #Supprime les titres
        corpus = supprChapterNum(corpus)                        #Supprime les numéros de chapitres
        corpus = supprCutSentences(corpus)                      #Supprime les phrases coupées
        corpus = re.sub(r'\s+', ' ', corpus)                    #Remplace '/n', '/t', ' ' isolé comme groupé par un espace
        corpus = removeChar(corpus)

        #-----------------------------------ECRITURE---------------------------------------

        output_path = os.path.join('./txt/corpus_classique/', pdf.replace('.pdf', '.txt'))
        with open(output_path, 'w', encoding="utf-8") as f:
            f.write(corpus)
