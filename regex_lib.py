from automaton_stuff import Automaton, DFA, NFA
from automaton_stuff.algos import (
    create_DFA_from_rex,
    create_NFA_from_rex,
    convert_NFA_to_NFA_without_eps
)
from automaton_stuff.utils.regex_utils import expand_plus, locate_union_symb
from automaton_stuff.utils.visualization import plot_automaton


auto = create_NFA_from_rex('ab.de')
auto = convert_NFA_to_NFA_without_eps(auto)



auto = create_DFA_from_rex('ab.?de')
plot_automaton(auto)

auto.is_valid_input('abcde')

