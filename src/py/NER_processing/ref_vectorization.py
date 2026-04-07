import json
from tqdm import tqdm 
from sentence_transformers import SentenceTransformer

input_file = "./json/reference_words_to_categorizing_relations.json"
output_file = "./json/reference_embeddings_to_categorizing_relations.json"
st = SentenceTransformer("dangvantuan/sentence-camembert-large")

jsonFile = {
    "professionnal": {"noun": [], "adjective": [], "verb": []},
    "friendly": {"noun": [], "adjective": [], "verb": []},
    "romance": {"noun": [], "adjective": [], "verb": []}
}

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for relation, categories in data.items():
    print(f"\nRelation : {relation}")
    for category, words in categories.items():
        for word in tqdm(words, desc=f"{relation} - {category}"):
            embedding = st.encode(word).tolist()
            jsonFile[relation][category].append(embedding)
            
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(jsonFile, f, ensure_ascii=False, indent=4)

print("JSON généré :", output_file)