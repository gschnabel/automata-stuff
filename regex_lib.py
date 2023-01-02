import re
import matplotlib.pyplot as plt
import networkx as nx
from automaton import Automaton
from automaton_algos import (
    rex_to_nfa,
    duplicate_automaton_part,
    clone_automaton_without_eps_transitions,
)




auto = Automaton()
auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
# auto.add_transition(3, 0, 'x')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')

auto.remove_transition(0, 3, 'a')
auto.remove_state(0)
auto.list_transitions()

duplicate_automaton_part(auto, 0)
auto.list_transitions()

auto = Automaton()
rex_to_nfa(auto, '(abc|(12)+3)')
clone_auto = clone_automaton_without_eps_transitions(auto)

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

