import matplotlib.pyplot as plt
import networkx as nx


def plot_automaton(automaton):
    plot_auto = automaton
    edges = list(plot_auto.list_transitions(symbols_in_dict=True))
    G = nx.DiGraph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 10))
    nx.draw(
        G, pos, edge_color='black', width=1, linewidths=1,
        node_size=500, node_color='pink', alpha=0.9,
        labels={node: node for node in G.nodes()},
        connectionstyle="arc3,rad=0.1"
    )
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=plot_auto.list_transitions(symbols_in_dict=True),
        font_color='red',
        label_pos=0.4
    )
    plt.axis('off')
    plt.show()
