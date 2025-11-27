import fitz
import re
import os



#-----------------------------------FUNCTIONS---------------------------------------


# Remove incomplete sentences
def supprCutSentences(texte):
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
def supprPartsTitle(texte):
    texte = re.sub(r'\n[A-ZÈ]+ PART \n \n \n[A-ZÀÂÇÉÈÊËÎÏÔÙÛ ]+', '', texte)
    return texte

# Remove chapter numbers
def supprChapterNum(texte):
    texte = re.sub(r'\n\b[IVXLCDM]+(?!\')\b \n', '', texte)
    return texte

# HANDLE DIALOGUES FUNCTION

# FUNCTION TO RETRIEVE WORDS NOT READ BY FITZ

# FUNCTION TO RETRIEVE INCOMPLETE WORDS (intended by the author)