import re, os


origin_folder = './txt/corpus_kaggle/prelude_a_fondation/origin'
modify_folder = './txt/corpus_kaggle/prelude_a_fondation/modify'

for file in os.listdir(origin_folder):

    origin_file = os.path.join(origin_folder, file)
    modify_file = os.path.join(modify_folder, file)

    f = open(origin_file, 'r', encoding="utf-8")
    corpus = f.read()
    f.close()

    corpus = re.sub(r'\n', ' ', corpus)
    corpus = re.sub(r'’', '\'', corpus)
    corpus = re.sub(r' {2,}', '', corpus)

    f = open(modify_file, 'w', encoding="utf-8")
    f.write(corpus)
    f.close()