import re
import matplotlib.pyplot as plt
import networkx as nx
from automaton import Automaton


auto = Automaton()
auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
# auto.add_transition(3, 0, 'x')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')

auto.remove_transition(0, 3, 'a')
auto.remove_state(0)
auto.list_transitions()

auto.duplicate_automaton_part(0)
auto.list_transitions()
auto.merge_states(3, 4)

auto.to_dfa()

'abc(uvw|123)'
'(abc|(12)+3)'


auto = Automaton()
auto.rex_to_nfa('(abc|(12)+3)')
auto.remove_eps_transitions()
edges = list(auto.list_transitions())
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
    edge_labels=auto.list_transitions(),
    font_color='red',
)
plt.axis('off')
plt.show()


