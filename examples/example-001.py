from automaton_stuff import Automaton
from automaton_stuff.utils.visualization import plot_automaton


# create an automaton manually
auto = Automaton()
auto.create_state(0)
auto.create_state(1)
auto.create_state(2)
auto.create_state(3)
auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')

print('States in automaton: ')
print(auto.list_states())

print('Transitions in automaton: ')
print(auto.list_transitions())

plot_automaton(auto)

print('Removoing state 0')
auto.remove_state(0)
print('Removing transitions from 1 to 3 for symbol b')
auto.remove_transition(1, 3, 'b')
print('Remaining states: ')
print(auto.list_states())
print('Remaining transitions: ')
print(auto.list_transitions())
