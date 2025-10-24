import spacy as sp

f = open('src/txt/Fondation.txt', 'r', encoding="utf-8")
texte = f.read()
f.close()

nlp = sp.load("fr_core_news_lg")
doc = nlp(texte)



#------------------------------EXPLIQUE LES TAGS FINS---------------------------------



# tags_uniques = sorted(set([token.tag_ for token in doc]))

# print("Liste des tags rencontrés et leurs explications :\n")
# for tag in tags_uniques:
#     explication = sp.explain(tag)
#     if explication is None:
#         explication = "Pas d'explication disponible (morphologie fine : " + tag + ")"
#     print(f"{tag:25} -> {explication}")



#------------------------------ANALYSEUR DE PHRASES---------------------------------



# texte = '''Vous ne pouvez songer à briguer sérieusement le poste de Maire. L'enthousiasme populaire est une force puissante, mais éphémère. - En effet ! dit Mallow, aussi devons-nous l'entretenir ; le meilleur moyen d'y parvenir me semble être de continuer l'exhibition. - Qu'allez-vous faire maintenant ? - Vous allez arrêter Publis Manlio et Jorane Sutt... - Comment ? - Vous avez bien entendu. Que le Maire les fasse arrêter ! Peu m'importent les menaces que vous emploierez. Je tiens la foule... pour aujourd'hui, en tout cas. Il n'osera pas l'affronter. - Mais sous quel prétexte les arrêter, mon cher ? - Sous le meilleur. Ils ont incité le clergé des planètes extérieures à prendre parti dans les querelles de la Fondation. C'est interdit depuis Seldon. Accusez-les d'atteinte à la sûreté de l'Etat.'''

# nlp = sp.load("fr_core_news_sm")
# doc = nlp(texte)
# for token in doc:
#     print(f"{token.text:<15}{token.lemma_:<15}{token.pos_:<10}{token.tag_:<10}{token.dep_:<10}{token.shape_:<10}{token.is_alpha:<10}{token.is_stop:<10}")