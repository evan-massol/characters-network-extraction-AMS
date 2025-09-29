import fitz
import re
import os



#-----------------------------------FONCTIONS---------------------------------------



def pdf_to_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_textpage().extractText()
            text += " -_ENDPAGE_- "
    return text

def supprCutSentences(texte):
    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):             #On commence par la fin pour ne pas perturber les indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        last_ponct = max(avant.rfind('.'), avant.rfind('!'), avant.rfind('?'))
        if last_ponct != -1:
            avant = avant[:last_ponct+1]        #On supprime après la dernière ponctuation
        else:
            avant = ""

        texte = avant + " -_ENDPAGE_- " + apres #On garde les marqueurs pour traiter les phrases post marqueurs

    matches = list(re.finditer(r"( -_ENDPAGE_- )", texte))
    for match in reversed(matches):                       #On commence par le début pour ne pas perturber les indices
        avant = texte[:match.start()]
        apres = texte[match.end():]
        if len(apres)!=0:
            premiere_lettre = next((c for c in apres if c.isalpha()))
            if not premiere_lettre.isupper():              #Si pas de majuscule juste après le marqueur
                apres_poncts = [apres.find('.'), apres.find('!'), apres.find('?')]
                if not all(x == -1 for x in apres_poncts):
                    apres_poncts = [x for x in apres_poncts if x != -1]
                first_ponct = min(apres_poncts)
                if first_ponct != -1:
                    apres = apres[first_ponct+1:]   #On supprime avant la première ponctuation
                else:
                    apres = ""

        texte = avant + apres

    return texte

def supprPartsTitle(texte):
    texte = re.sub(r'\n[A-ZÈ]+ PARTIE \n \n \n[A-ZÀÂÇÉÈÊËÎÏÔÙÛ ]+', '', texte)
    return texte

def supprChapterNum(texte):
    texte = re.sub(r'\n\b[IVXLCDM]+(?!\')\b \n', '', texte)
    return texte

# FAIRE FONCTION GERER DIALOGUES

# FAIRE FONCTION RECUPERER MOTS NON LU PAR FITZ

# FAIRE FONCTION RECUPERER MOTS INCOPLETS (voulu par l'auteur) 



#------------------------------TRAITEMENT DU TEXTE---------------------------------



corpus = pdf_to_text("./.venv/src/pdf/Fondation_sample.pdf") 
corpus = re.sub(r'\ufffd\s*\d+\s*\ufffd', ' ', corpus)  #Supprime les numéros de pages
corpus = supprPartsTitle(corpus)                        #Supprime les titres
corpus = supprChapterNum(corpus)                        #Supprime les numéros de chapitres
corpus = supprCutSentences(corpus)                      #Supprime les phrases coupées
corpus = re.sub(r'\s+', ' ', corpus)                    #Remplace '/n', '/t', ' ' isolé comme groupé par un espace



#-----------------------------------ECRITURE---------------------------------------



f = open('./.venv/src/txt/Fondation.txt', 'w', encoding="utf-8")
f.write(corpus)
f.close()