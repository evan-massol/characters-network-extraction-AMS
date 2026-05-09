import json
import math
import os
from pathlib import Path
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from collections import Counter, defaultdict

import spacy as sp
from unidecode import unidecode


def _load_antidict():
    """Load anti-dictionary words with resilient path resolution."""
    candidates = [
        Path("./fonctionnels_fr.txt"),
        Path("./src/fonctionnels_fr.txt"),
        Path(__file__).resolve().parents[1] / "fonctionnels_fr.txt",
    ]

    for candidate in candidates:
        if candidate.exists():
            with open(candidate, 'r', encoding='utf-8') as f:
                return {unidecode(line.strip().lower()) for line in f if line.strip()}

    print("Warning: anti-dictionary file not found; continuing without anti-dictionary filtering.")
    return set()


def _split_text_into_chapters(text, min_words_per_chunk=1800):
    """Split text into chapters; fallback to fixed-size chunks when markers are missing."""
    text = text.strip()
    if not text:
        return []

    chapter_marker_patterns = [
        r"(?im)^\s*(chapitre|chapter)\s+[0-9ivxlcdm]+\b.*$",
        r"(?m)^\s*[IVXLCDM]{1,8}\s*$",
    ]

    for pattern in chapter_marker_patterns:
        matches = list(re.finditer(pattern, text))
        if len(matches) >= 2:
            boundaries = [m.start() for m in matches] + [len(text)]
            chapters = []
            for i in range(len(boundaries) - 1):
                chapter = text[boundaries[i]:boundaries[i + 1]].strip()
                if chapter:
                    chapters.append(chapter)
            if chapters:
                return chapters

    words = text.split()
    if not words:
        return []

    chunks = []
    for start in range(0, len(words), min_words_per_chunk):
        chunk_words = words[start:start + min_words_per_chunk]
        if chunk_words:
            chunks.append(" ".join(chunk_words))

    return chunks


def is_valid_entity(text, anti_dict=None):
    """Validation for person entities with anti-dictionary filtering."""
    text = text.strip()
    unicode_dashes = "-–—―‒‑⁻−"
    if not re.search(r'[a-zA-ZÀ-ÿ]', text):
        return False
    if any(dash in text for dash in unicode_dashes):
        return False
    if re.search(r"[a-z][A-Z]|[A-Z]{3,}|[a-z]{1,2}'[a-z]{1,2}", text):
        return False
    if not re.match(r'^[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\-\s\']{2,}$', text):
        return False

    allowed_particles = {"de", "du", "des", "d", "d'", "le", "la", "les", "l", "l'", "et", "van", "von", "da", "del", "di"}
    tokens = [tok.strip(" ,;:!?\"()[]{}") for tok in text.split() if tok.strip()]
    for token in tokens:
        token_norm = unidecode(token.lower())
        if token_norm in allowed_particles:
            continue
        if not re.match(r"^[A-ZÀ-Ÿ][a-zà-ÿA-ZÀ-Ÿ\-']*$", token):
            return False

    if anti_dict is not None:
        normalized = unidecode(text.lower()).strip()
        if normalized in anti_dict:
            return False

    return True


def build_entity_aliases(entities_list, entity_type="PER"):
    """Simple alias grouping: map short forms to longer canonical names."""
    sorted_entities = sorted(set([e.text for e in entities_list]), key=len, reverse=True)
    alias_map = {}

    for entity in sorted_entities:
        if entity in alias_map:
            continue

        canonical = entity
        alias_map[entity] = canonical
        words = entity.split()

        if len(words) >= 2:
            last_word = words[-1]
            if len(last_word) > 2 and last_word in sorted_entities and last_word != entity:
                alias_map[last_word] = canonical

            first_word = words[0]
            if len(words) == 2 and len(first_word) > 2 and first_word in sorted_entities and first_word != entity:
                alias_map[first_word] = canonical

    return alias_map


def merge_entity_counts(entities_list, alias_map):
    """Merge entity counts according to alias map."""
    merged_counts = Counter()
    for entity in entities_list:
        canonical = alias_map.get(entity.text, entity.text)
        merged_counts[canonical] += 1
    return merged_counts


def mapping_entity(entities_list, alias_map):
    """Map each entity occurrence to canonical form with token span."""
    entity_map = {}
    for entity in entities_list:
        canonical = alias_map.get(entity.text, entity.text)
        entity_map[(entity.text, entity.start, entity.end)] = canonical
    return entity_map


def build_entity_relation(entity_map, max_token_distance=25):
    """Build weighted relations based on nearby entity co-occurrences in token space."""
    relations_map = defaultdict(int)
    sorted_entities = sorted(entity_map.items(), key=lambda item: item[0][1])

    for i, entity in enumerate(sorted_entities):
        for neighbor in sorted_entities[i + 1:]:
            if neighbor[0][1] - entity[0][2] > max_token_distance:
                break
            left = entity[1]
            right = neighbor[1]
            if left == right:
                continue
            key = tuple(sorted((left, right)))
            relations_map[key] += 1

    return relations_map

def load_entities_output(filepath="./json/entities_output.json"):
    """Load entities output JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _extract_entities_from_txt(filepath, nlp, entity_type="PER"):
    """Extract entities from one text file and return a chapter-like structure."""
    with open(filepath, 'r', encoding='utf-8') as f:
        corpus = f.read()

    doc = nlp(corpus)
    entities = []

    for ent in doc.ents:
        if ent.label_ != entity_type:
            continue
        if entity_type == "PER" and not is_valid_entity(ent.text):
            continue
        entities.append(ent)

    alias_map = build_entity_aliases(entities, entity_type=entity_type)
    counts = merge_entity_counts(entities, alias_map)

    chapter_entity_data = {
        "book_code": Path(filepath).stem,
        "file": os.path.basename(filepath),
        "chapter_number": 0,
        "entities": {
            "PER": [],
            "MISC": [],
        },
        "_doc": doc,
        "_alias_map": alias_map,
    }

    chapter_entity_data["entities"][entity_type] = [
        {"name": name, "type": entity_type, "count": count}
        for name, count in sorted(counts.items())
    ]

    return chapter_entity_data


def load_entities_from_corpus(corpus_dir="./txt/corpus_classique", target_file=None, entity_type="PER", model_name="fr_core_news_lg"):
    """Load entities-like structure directly from corpus text files."""
    nlp = sp.load(model_name)

    if target_file:
        txt_files = [target_file]
    else:
        txt_files = sorted(
            [
                os.path.join(corpus_dir, f)
                for f in os.listdir(corpus_dir)
                if f.endswith('.txt')
            ]
        )

    if not txt_files:
        raise FileNotFoundError(f"No .txt file found in '{corpus_dir}'.")

    entities_output = []
    for txt_file in txt_files:
        chapter_data = _extract_entities_from_txt(txt_file, nlp=nlp, entity_type=entity_type)
        entities_output.append(chapter_data)

    return entities_output

def build_global_ner_graph(entities_output, entity_type="PER", min_count=2, book_filter=None, chapter_filter=None):
    """Build global graph of named entities across all chapters."""
    G = nx.Graph()
    global_counts = Counter()
    entity_chapters = {}
    
    for chapter in entities_output:
        if book_filter and chapter["book_code"] != book_filter:
            continue
        if chapter_filter is not None and chapter["chapter_number"] != chapter_filter:
            continue
        for entity in chapter["entities"][entity_type]:
            name = entity["name"]
            count = entity["count"]
            global_counts[name] += count
            
            if name not in entity_chapters:
                entity_chapters[name] = []
            entity_chapters[name].append({
                "book": chapter["book_code"],
                "chapter": chapter["chapter_number"],
                "count": count
            })
    
    # Add nodes (min_count threshold)
    for entity, count in global_counts.items():
        if count >= min_count:
            G.add_node(entity, 
                      count=count, 
                      appearances=len(entity_chapters[entity]),
                      chapters=entity_chapters[entity])
    
    # Add edges between entities appearing in same chapters
    nodes = list(G.nodes())
    for i, entity1 in enumerate(nodes):
        chapters1 = set((ch["book"], ch["chapter"]) for ch in entity_chapters[entity1])
        
        for entity2 in nodes[i+1:]:
            chapters2 = set((ch["book"], ch["chapter"]) for ch in entity_chapters[entity2])
            common_chapters = chapters1 & chapters2
            
            if common_chapters:
                G.add_edge(entity1, entity2, weight=len(common_chapters))
    
    return G


def build_graph_from_single_txt(txt_path, entity_type="PER", min_count=2, model_name="fr_core_news_lg"):
    """Build one graph from one text file, aggregating chapter-level counts and relations."""
    nlp = sp.load(model_name)
    anti_dict = _load_antidict()

    with open(txt_path, 'r', encoding='utf-8') as f:
        corpus = f.read()

    chapters = _split_text_into_chapters(corpus)
    if not chapters:
        return nx.Graph()

    chapter_entities = []
    all_entities = []

    for chapter_text in chapters:
        doc = nlp(chapter_text)
        entities = []
        for ent in doc.ents:
            if ent.label_ != entity_type:
                continue
            if entity_type == "PER" and not is_valid_entity(ent.text, anti_dict=anti_dict):
                continue
            entities.append(ent)

        chapter_entities.append(entities)
        all_entities.extend(entities)

    alias_map = build_entity_aliases(all_entities, entity_type=entity_type)

    global_counts = Counter()
    entity_chapters = defaultdict(set)
    edge_weights = defaultdict(int)

    for chapter_idx, entities in enumerate(chapter_entities, start=1):
        if not entities:
            continue

        chapter_counts = merge_entity_counts(entities, alias_map)
        for canonical_name, count in chapter_counts.items():
            global_counts[canonical_name] += count
            entity_chapters[canonical_name].add(chapter_idx)

        entity_map = mapping_entity(entities, alias_map)
        chapter_relations = build_entity_relation(entity_map)
        for edge_key, weight in chapter_relations.items():
            edge_weights[edge_key] += weight

    G = nx.Graph()
    for canonical_name, count in global_counts.items():
        if count >= min_count:
            G.add_node(
                canonical_name,
                count=count,
                appearances=len(entity_chapters[canonical_name]),
                chapters=sorted(entity_chapters[canonical_name]),
            )

    for (src, dst), weight in edge_weights.items():
        if src in G and dst in G:
            G.add_edge(src, dst, weight=weight)

    return G

def visualize_graph(G, title="Named entities graph", figsize=(16, 12), 
                   node_size_multiplier=25, layout="kamada_kawai", font_size=7, edge_width_multiplier=15, node_border_width=1, use_sqrt_for_nodes=True):
    """Visualize graph with matplotlib."""
    fig, ax = plt.subplots(figsize=figsize, facecolor='black')
    ax.set_facecolor('black')
    
    # Layout selection
    if layout == "spring":
        pos = nx.spring_layout(G, k=6.0, iterations=200, seed=42)
        for node in pos:
            pos[node] = pos[node] * 2.5
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G, scale=5.0)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G, k=2.0, iterations=200)
        for node in pos:
            pos[node] = pos[node] * 2.5
    
    # Calculate node sizes - use sqrt for global graph, raw values for chapters
    if use_sqrt_for_nodes:
        node_sizes = [math.sqrt(G.nodes[node].get('count', 1)) * node_size_multiplier for node in G.nodes()]
    else:
        node_sizes = [G.nodes[node].get('count', 1) * node_size_multiplier for node in G.nodes()]
    
    node_colors = [G.nodes[node].get('appearances', 1) for node in G.nodes()]
    
    # Edge widths proportional to weight
    edges = G.edges()
    weights = [G[u][v].get('weight', 1) for u, v in edges]
    
    if weights:
        min_weight = min(weights)
        max_weight = max(weights)
        edge_widths = [0.5 + (w - min_weight) / (max_weight - min_weight) * edge_width_multiplier if max_weight > min_weight else 1.0 
                       for w in weights]
    else:
        edge_widths = []
    
    # Draw graph
    nx.draw_networkx_nodes(G, pos, 
                          node_size=node_sizes,
                          node_color=node_colors,
                          cmap=plt.get_cmap('cool'),
                          alpha=0.9,
                          edgecolors='white',
                          linewidths=node_border_width,
                          ax=ax)
    
    nx.draw_networkx_edges(G, pos, 
                          width=edge_widths,
                          alpha=0.4,
                          edge_color='red',
                          ax=ax)
    
    # Labels with offset
    pos_labels = {node: (x, y - 0.12) for node, (x, y) in pos.items()}
    
    nx.draw_networkx_labels(G, pos_labels, 
                           font_size=font_size,
                           font_weight='bold',
                           font_color='white',
                           bbox=dict(facecolor='black', alpha=0.7, edgecolor='white', pad=2, boxstyle='round,pad=0.3'),
                           ax=ax)
    
    ax.set_title(title, fontsize=16, fontweight='bold', color='white')
    plt.axis('off')
    plt.tight_layout()
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.get_cmap('cool'), 
                               norm=Normalize(vmin=min(node_colors), vmax=max(node_colors)))
    cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04, orientation='horizontal', location='bottom')
    cbar.ax.xaxis.set_ticks_position('top')
    cbar.ax.xaxis.set_label_position('top')
    cbar.ax.set_xlabel('Number of chapters', labelpad=10, color='white')
    cbar.ax.tick_params(colors='white')
    for spine in cbar.ax.spines.values():
        spine.set_edgecolor('white')
    
    return plt

def print_graph_stats(G):
    """Print graph statistics."""
    print("\n" + "="*80)
    print("GRAPH STATISTICS")
    print("="*80)
    print(f"Nodes (entities): {G.number_of_nodes()}")
    print(f"Edges (relationships): {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.4f}")
    
    if G.number_of_nodes() > 0:
        print(f"\nAverage degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")
        
        print("\n" + "-"*80)
        print("TOP 10 BY OCCURRENCES:")
        print("-"*80)
        sorted_by_count = sorted(G.nodes(data=True), key=lambda x: x[1].get('count', 0), reverse=True)[:10]
        for i, (entity, data) in enumerate(sorted_by_count, 1):
            print(f"{i:2d}. {entity:<30} - {data['count']:4d} occurrences, {data['appearances']:2d} chapters")
        
        print("\n" + "-"*80)
        print("TOP 10 BY CONNECTIVITY:")
        print("-"*80)
        sorted_by_degree = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
        for i, (entity, degree) in enumerate(sorted_by_degree, 1):
            count = G.nodes[entity]['count']
            print(f"{i:2d}. {entity:<30} - {degree:3d} connections, {count:4d} occurrences")


def main():
    """Main function."""
    print("\nGenerating NER graphs for corpus_classique...\n")

    try:
        corpus_candidates = [
            Path("./txt/corpus_classique"),
            Path("./src/txt/corpus_classique"),
            Path(__file__).resolve().parents[1] / "txt" / "corpus_classique",
        ]
        corpus_dir = next((str(p) for p in corpus_candidates if p.exists()), None)

        if corpus_dir is None:
            raise FileNotFoundError("Unable to locate corpus_classique directory.")

        txt_files = sorted(
            [
                os.path.join(corpus_dir, filename)
                for filename in os.listdir(corpus_dir)
                if filename.endswith(".txt")
            ]
        )

        if not txt_files:
            raise FileNotFoundError(f"No .txt file found in '{corpus_dir}'.")

        os.makedirs("./graphs", exist_ok=True)

        for txt_path in txt_files:
            corpus_name = Path(txt_path).stem
            print(f"\nProcessing: {corpus_name}")

            graph = build_graph_from_single_txt(
                txt_path=txt_path,
                entity_type="PER",
                min_count=3,
                model_name="fr_core_news_lg",
            )

            print_graph_stats(graph)
            plt_obj = visualize_graph(graph, title=f"Character Network - {corpus_name}")

            png_path = f"./graphs/ner_graph_{corpus_name}.png"
            graphml_path = f"./graphs/ner_graph_{corpus_name}.graphml"

            plt_obj.savefig(png_path, dpi=300, bbox_inches='tight')
            plt_obj.close()
            print(f"Graph saved: {png_path}")

            graph_export = graph.copy()
            for node in graph_export.nodes():
                if 'chapters' in graph_export.nodes[node] and isinstance(graph_export.nodes[node]['chapters'], list):
                    graph_export.nodes[node]['chapters'] = json.dumps(graph_export.nodes[node]['chapters'])

            nx.write_graphml(graph_export, graphml_path)
            print(f"Graph exported: {graphml_path}")

        print("\nAll corpus_classique graphs generated.")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


