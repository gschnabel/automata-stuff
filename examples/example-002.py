from automata_stuff.utils.visualization import plot_automaton
from automata_stuff.algos import (
    create_DFA_from_rex,
    create_NFA_from_rex,
    convert_NFA_to_NFA_without_eps,
    convert_NFA_without_eps_to_DFA,
    convert_DFA_to_minimal_DFA
)


# create a Non-Deterministic Finite Automaton (NFA)
# from a regular expression
auto = create_NFA_from_rex(r'(a\+b|ab|a+)+')
plot_automaton(auto)

# remove the epsilon transitions
auto = convert_NFA_to_NFA_without_eps(auto)
plot_automaton(auto)

# we have still an instance of `Automaton`
print(type(auto))

# convert the NFA to a DFA
auto = convert_NFA_without_eps_to_DFA(auto)
plot_automaton(auto)

# now we have a special case of an automaton,
# a Deterministic Finite Automaton (DFA)
print(type(auto))

# convert the DFA to a minimal DFA
auto = convert_DFA_to_minimal_DFA(auto)
plot_automaton(auto)

# the same result, the construction of a
# minimal DFA can be achieved quicker
# by using the following function
auto = create_DFA_from_rex(r'(a\+b|ab|a+)+')
plot_automaton(auto)

# checking if a character sequence is a valid
# input for the DFA
auto.is_valid_input('a+baaaaab')
