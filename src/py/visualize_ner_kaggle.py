import json
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from collections import Counter

def load_entities_output(filepath="./json/entities_output.json"):
    """Load entities output JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

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
    print("\nGenerating NER graph...\n")
    
    try:
        entities_output = load_entities_output()
        
        # ===== GLOBAL GRAPH =====
        print("Building characters graph (Prelude to Foundation)...")
        G_per = build_global_ner_graph(entities_output, entity_type="PER", min_count=3, book_filter="paf")
        
        print_graph_stats(G_per)
        
        print("\nGenerating global visualization...")
        plt_obj = visualize_graph(G_per, title="Character Network - Prelude to Foundation", layout="spring")
        
        output_path = "./graphs/ner_graph_persons_paf.png"
        plt_obj.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved: {output_path}")
        
        plt_obj.show()
        
        # Export to GraphML
        G_per_export = G_per.copy()
        for node in G_per_export.nodes():
            if 'chapters' in G_per_export.nodes[node]:
                G_per_export.nodes[node]['chapters'] = json.dumps(G_per_export.nodes[node]['chapters'])
        
        nx.write_graphml(G_per_export, "./graphs/ner_graph_persons_paf.graphml")
        print(f"Graph exported: ./graphs/ner_graph_persons_paf.graphml")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        print("   Make sure to run FirstInLeaderboard.py first.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


