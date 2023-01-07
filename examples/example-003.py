from automata_stuff.algos import create_DFA_from_rex
from automata_stuff.algos.checking import is_subautomaton


rex1 = 'abc_(uv|xy)+_def'
rex2 = 'abc_xyuv_def'

auto1 = create_DFA_from_rex(rex1)
auto2 = create_DFA_from_rex(rex2)

# returns true because every string
# accepted by the regular expression
# rex2 is also accepted by rex1
is_subautomaton(auto2, auto1)

# returns false because not every
# there are strings accepted by rex1
# that are not accepted by rex2
is_subautomaton(auto1, auto2)
