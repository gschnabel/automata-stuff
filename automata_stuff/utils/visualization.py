import matplotlib.pyplot as plt
import networkx as nx


def plot_automaton(automaton, abbreviate_all=True):
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
    alphabet = automaton.list_symbols(include_eps=False)
    raw_edge_labels = plot_auto.list_transitions(symbols_in_dict=True)
    edge_labels = dict()
    for curtrans, symset in raw_edge_labels.items():
        if abbreviate_all and not alphabet.difference(symset):
            newsymset = symset.difference(alphabet)
            newsymset.add('any')
        else:
            newsymset = symset.copy()
        edge_labels[curtrans] = newsymset
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_color='red',
        label_pos=0.4
    )
    plt.axis('off')
    plt.show()
