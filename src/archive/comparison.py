import spacy as sp
import stanza
import re

text = """Le 12 mars 2023, Marie Dupont arriva à Paris pour rencontrer le directeur de l’UNESCO.
« Ne perdez pas de temps », lui avait dit Paul en souriant.
Marie expliqua ensuite qu’elle avait travaillé chez Google pendant cinq ans avant de rejoindre l’université de Lyon.
Appelle immédiatement le service juridique et prépare le dossier.
Selon le rapport publié par l’Organisation mondiale de la santé, la situation reste préoccupante.
« Nous devons agir maintenant », déclara le ministre de la Santé devant les journalistes.
Jean pensa que cette réunion à Bruxelles serait décisive pour l’avenir du projet.
N’oubliez pas d’envoyer le courriel à Sophie avant vendredi.
Le professeur Martin affirma que ses recherches en linguistique computationnelle commenceraient en janvier 2024.
« Faites attention aux détails », répéta-t-il calmement.
"""
text = re.sub(r'[\r\n]+', '', text)
text = re.sub(r'[\r-]+', ' ', text)

#------------------------------SPACY PROCESSING---------------------------------

nlp_spacy = sp.load("fr_core_news_lg")
doc_spacy = nlp_spacy(text)

spacy_tokens = [(token.text, token.pos_) for token in doc_spacy]
spacy_persons = [ent.text for ent in doc_spacy.ents if ent.label_ == "PER"]

print("=== spaCy : ENTITÉS NOMMÉES ===")
for ent in doc_spacy.ents:
    if ent.label == "PER":
        print(f"{ent.text:<20}{ent.label_:<5}")

print("\n=== spaCy : TOKENS / POS ===")
for token in doc_spacy:
    print(f"{token.text:<15}{token.pos_:<10}{token.tag_:<10}{token.lemma_:<15}")



#------------------------------STANZA PROCESSING---------------------------------



nlp_stanza = stanza.Pipeline(
    lang="fr",
    processors="tokenize,pos,ner",
    use_gpu=False
)
doc_stanza = nlp_stanza(text)

doc_stanza = nlp_stanza(text)
stanza_tokens = [(word.text, word.upos) 
                 for sent in doc_stanza.sentences 
                 for word in sent.words]
stanza_persons = [ent.text for ent in doc_stanza.ents if ent.type == "PER"]

print("=== Stanza : ENTITÉS NOMMÉES ===")
for ent in doc_stanza.ents:
    if ent.type == "PER":
        print(f"{ent.text:<20}{ent.type:<5}")

print("\n=== Stanza : TOKENS / POS ===")
for sentence in doc_stanza.sentences:
    for word in sentence.words:
        print(f"{word.text:<15}{word.upos:<10}{word.xpos}")



#------------------------------COMPARAISON---------------------------------

# --- Statistiques ---

print("\n=== Statistiques spaCy ===")
print(f"Tokens : {len(spacy_tokens)}")
print(f"Personnages détectés : {len(spacy_persons)}")

print("\n=== Statistiques Stanza ===")
print(f"Tokens : {len(stanza_tokens)}")
print(f"Personnages détectés : {len(stanza_persons)}")