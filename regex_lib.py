import re
import matplotlib.pyplot as plt
import networkx as nx
from automaton_stuff import Automaton, NFA, DFA
from automaton_stuff.algos import (
    create_NFA_from_rex,
    convert_NFA_to_NFA_without_eps,
    convert_NFA_without_eps_to_DFA,
    convert_DFA_to_minimal_DFA,
    convert_NFA_to_DFA
)
from automaton_stuff.regex_utils import expand_plus, locate_union_symb

# basic checks of automaton
auto = Automaton()
auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
# auto.add_transition(3, 0, 'x')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')
auto.list_transitions()

# basic checking of NFA-delta to DFA
auto = create_NFA_from_rex(r'(a\+b|ab|a+)+')
clone_auto = convert_NFA_to_NFA_without_eps(auto)
clone_auto = convert_NFA_without_eps_to_DFA(clone_auto)
clone_auto = convert_DFA_to_minimal_DFA(clone_auto)

clone_auto = convert_NFA_to_DFA(auto)


plot_auto = clone_auto
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

clone_auto.list_transitions(source_states=((12,13,)))

