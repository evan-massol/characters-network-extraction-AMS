import pandas as pd
import networkx as nx
import io
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from collections import Counter
import math

def load_graph_from_csv(csv_path, graph_id="Fondation"):
    """
    Reconstruit un graphe NetworkX à partir du CSV contenant une colonne 'graphml'.
    
    Parameters
    ----------
    csv_path : str
        Chemin vers le fichier CSV
    graph_id : str
        Valeur de l'index 'ID' correspondant au graphe à charger
    
    Returns
    -------
    G : networkx.Graph
    """
    
    # Lecture du CSV
    df = pd.read_csv(csv_path, index_col="ID")
    
    if graph_id not in df.index:
        raise ValueError(f"Graphe '{graph_id}' introuvable dans le CSV")
    
    # Récupération du GraphML (stocké comme string)
    graphml_str = df.loc[graph_id, "graphml"]
    
    # Conversion string -> fichier mémoire
    # graphml_io = io.StringIO(graphml_str)
    
    # Reconstruction du graphe
    G = nx.parse_graphml(graphml_str)
    
    return G

def fix_graph_types(G):
    """
    Convertit les attributs numériques stockés en strings en int/float.
    """
    
    for node, data in G.nodes(data=True):
        for key in ["count", "appearances"]:
            if key in data:
                try:
                    data[key] = int(data[key])
                except ValueError:
                    pass
    
    for u, v, data in G.edges(data=True):
        if "weight" in data:
            try:
                data["weight"] = float(data["weight"])
            except ValueError:
                pass

def visualize_graph(G, title="Named entities graph", figsize=(16, 12), 
                   node_size_multiplier=25, layout="kamada_kawai", font_size=7, edge_width_multiplier=15, node_border_width=1, use_sqrt_for_nodes=True):
    """Visualize graph with matplotlib."""
    fig, ax = plt.subplots(figsize=figsize, facecolor='black')
    ax.set_facecolor('black')
    
    # Layout selection
    if layout == "spring":
        pos = nx.spring_layout(G, k=1, iterations=200, seed=42)
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

    SPREAD = 1.5
    pos = {node: (x * SPREAD, y * SPREAD) for node, (x, y) in pos.items()}
    
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

def print_graph_stats_simplify(G):
    """Print graph statistics."""
    print("\n" + "="*80)
    print("GRAPH STATISTICS")
    print("="*80)
    print(f"Nodes (entities): {G.number_of_nodes()}")
    print(f"Edges (relationships): {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.4f}")


# Chargement du graphe
G = load_graph_from_csv(
    "./EvanMASSOL_MartinGERIS_Fondation.csv",
    graph_id="Fondation"
)

# Correction des types
fix_graph_types(G)

# Statistiques
print_graph_stats_simplify(G)

# Visualisation
graph = visualize_graph(
    G,
    title="Fondation – Graphe des entités nommées",
    layout="kamada_kawai",
    use_sqrt_for_nodes=True
)

graph.show()
