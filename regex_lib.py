import re
import matplotlib.pyplot as plt
import networkx as nx
from automaton import Automaton
from automaton_algos import (
    create_NFA_from_rex,
    duplicate_automaton_part,
    convert_NFA_to_NFA_without_eps,
    convert_NFA_without_eps_to_DFA,
    convert_DFA_to_minimal_DFA
)

# basic checks of automaton
auto = Automaton()
auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
# auto.add_transition(3, 0, 'x')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')
duplicate_automaton_part(auto, 0)
auto.list_transitions()

# basic checking of NFA-delta to DFA
auto = Automaton()
create_NFA_from_rex(auto, '(aaa|a+)')
clone_auto = convert_NFA_to_NFA_without_eps(auto)
clone_auto = convert_NFA_without_eps_to_DFA(clone_auto)
clone_auto = convert_DFA_to_minimal_DFA(clone_auto)
clone_auto = convert_DFA_to_minimal_DFA(clone_auto)


# basic checking of converting regular expression to NFA
auto = Automaton()
create_NFA_from_rex(auto, '(abc|(12)+3)')
clone_auto = convert_NFA_to_NFA_without_eps(auto)


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
)
nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=plot_auto.list_transitions(symbols_in_dict=True),
    font_color='red',
)
plt.axis('off')
plt.show()

clone_auto.list_transitions(source_states=((12,13,)))

