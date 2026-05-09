import os
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


RELATION_COLORS = {
    "professionnal": "#F4C430",
    "friendly": "#4FC3F7",
    "romance": "#EC407A",
}


def load_graph_from_csv(csv_path, graph_id="Fondation"):
    """Load the GraphML string from a relation CSV and rebuild a NetworkX graph."""
    df = pd.read_csv(csv_path, index_col="ID")
    if graph_id not in df.index:
        raise ValueError(f"Graph '{graph_id}' not found in {csv_path}")

    graphml_str = df.loc[graph_id, "graphml"]
    graph = nx.parse_graphml(graphml_str)

    for _, _, data in graph.edges(data=True):
        for key in ["weight", "professionnal", "friendly", "romance"]:
            if key in data:
                data[key] = float(data[key])

    return graph


def extract_edge_relations(graph):
    """Return relation data for each edge as a list of records."""
    records = []

    for source, target, data in graph.edges(data=True):
        professional = float(data.get("professionnal", 0))
        friendly = float(data.get("friendly", 0))
        romance = float(data.get("romance", 0))
        classified_total = professional + friendly + romance
        weight = float(data.get("weight", classified_total))

        if weight <= 0:
            continue

        records.append(
            {
                "relation": f"{source} - {target}",
                "professionnal": professional,
                "friendly": friendly,
                "romance": romance,
                "weight": weight,
                "classified_total": classified_total,
            }
        )

    return records


def plot_stacked_relation_bars(records, title, output_path, summary_output_path, normalize=True, figsize=None):
    """Plot stacked bars for relation categories."""
    if not records:
        print(f"No relation data to plot for {title}")
        return

    df = pd.DataFrame(records)
    df = df.sort_values("weight", ascending=False).reset_index(drop=True)

    summary_df = df.copy()
    safe_denominator = summary_df["classified_total"].replace(0, 1)
    summary_df["professionnal_pct"] = (summary_df["professionnal"] / safe_denominator) * 100.0
    summary_df["friendly_pct"] = (summary_df["friendly"] / safe_denominator) * 100.0
    summary_df["romance_pct"] = (summary_df["romance"] / safe_denominator) * 100.0
    os.makedirs(Path(summary_output_path).parent, exist_ok=True)
    summary_df.to_csv(summary_output_path, index=False)

    if normalize:
        safe_denominator = df["classified_total"].replace(0, 1)
        for column in ["professionnal", "friendly", "romance"]:
            df[column] = (df[column] / safe_denominator) * 100.0
        ylabel = "Share of relation (%)"
    else:
        ylabel = "Relation count"

    if figsize is None:
        width = max(14, min(0.45 * len(df), 40))
        figsize = (width, 8)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")

    x = range(len(df))
    bottom = [0] * len(df)

    for column in ["professionnal", "friendly", "romance"]:
        ax.bar(
            x,
            df[column],
            bottom=bottom,
            color=RELATION_COLORS[column],
            label=column,
            width=0.8,
            edgecolor="black",
            linewidth=0.6,
        )
        bottom = [b + v for b, v in zip(bottom, df[column])]

    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["relation"], rotation=75, ha="right", fontsize=8)
    ax.tick_params(axis="y", colors="white")
    ax.tick_params(axis="x", colors="white")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(axis="y", alpha=0.2)

    # Show each edge weight over its bar.
    y_max = max(bottom) if bottom else 0
    for idx, value in enumerate(df["weight"]):
        ax.text(
            idx,
            y_max + (2 if normalize else 0.4),
            f"w={int(value)}",
            ha="center",
            va="bottom",
            fontsize=7,
            color="white",
            rotation=90,
        )

    if normalize:
        ax.set_ylim(0, max(110, y_max + 8))

    plt.tight_layout()
    os.makedirs(Path(output_path).parent, exist_ok=True)
    plt.savefig(output_path, dpi=300) #bbox_inches="tight"
    plt.close(fig)
    print(f"Saved: {output_path}")


def main():
    """Generate stacked relation bar charts for every processed relation CSV."""
    input_dir = Path("./src/csv/processed_relation")
    output_dir = Path("./src/graphs/relation_bars")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    for csv_path in csv_files:
        print(f"Processing {csv_path.stem}...")
        graph = load_graph_from_csv(csv_path)
        records = extract_edge_relations(graph)

        if not records:
            print(f"No usable edges in {csv_path.name}")
            continue

        output_path = output_dir / f"{csv_path.stem}_relations_stacked.png"
        summary_output_path = output_dir / f"{csv_path.stem}_relations_summary.csv"
        plot_stacked_relation_bars(
            records,
            title=f"Relation types - {csv_path.stem}",
            output_path=output_path,
            summary_output_path=summary_output_path,
            normalize=True,
        )


if __name__ == "__main__":
    main()