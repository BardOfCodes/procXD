"""example script to visualize a networkx graph using procXD."""

import networkx as nx
from procXD import SketchBuilder

if __name__ == "__main__":
    G = nx.gnp_random_graph(10, 0.3, directed=True)
    pos = nx.circular_layout(G)
    for node in G.nodes():
        G.nodes[node]['label'] = f'Node {node}'
        G.nodes[node]['pos'] = pos[node]
    SAVE_FILE = "examples/figures/network.excalidraw"
    sketch_builder = SketchBuilder(save_path=SAVE_FILE)
    sketch_builder.render_networkx_graph(G)
    sketch_builder.export_to_file()
