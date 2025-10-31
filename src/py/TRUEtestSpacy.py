import spacy as sp

f = open('txt/Fondation.txt', 'r', encoding="utf-8")
texte = f.read()
f.close()

nlp = sp.load("fr_core_news_lg")
doc = nlp(texte)



#------------------------------EXPLAIN FINE TAGS---------------------------------



# tags_uniques = sorted(set([token.tag_ for token in doc]))

# print("List of encountered tags and their explanations:\n")
# for tag in tags_uniques:
#     explanation = sp.explain(tag)
#     if explanation is None:
#         explanation = "No explanation available (fine morphology: " + tag + ")"
#     print(f"{tag:25} -> {explanation}")



#------------------------------SENTENCE ANALYZER---------------------------------



# texte = '''You cannot seriously consider running for Mayor. Popular enthusiasm is a powerful but ephemeral force. - Indeed! said Mallow, so we must maintain it; the best way to do so seems to me to continue the exhibition. - What are you going to do now? - You are going to arrest Publis Manlio and Jorane Sutt... - How? - You heard me. Let the Mayor have them arrested! I don't care what threats you use. I hold the crowd... for today, anyway. He won't dare face it. - But on what pretext to arrest them, my dear? - On the best. They have incited the clergy of the outer planets to take sides in the Foundation's quarrels. This has been forbidden since Seldon. Accuse them of endangering state security.'''

# nlp = sp.load("fr_core_news_sm")
# doc = nlp(texte)
# for token in doc:
#     print(f"{token.text:<15}{token.lemma_:<15}{token.pos_:<10}{token.tag_:<10}{token.dep_:<10}{token.shape_:<10}{token.is_alpha:<10}{token.is_stop:<10}")