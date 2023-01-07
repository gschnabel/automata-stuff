from ..DFA import DFA
from ..automaton import Automaton
from .conversion import convert_NFA_to_DFA
from .auxiliary import organize_transitions_by_symbols


def _is_subautomaton(
    auto1, auto2, curstate1, curstate2, visited=None
):
    visited = set() if visited is None else visited
    visited.add(curstate1)
    in_t1 = auto1.list_transitions(target_states=(curstate1,))
    in_t2 = auto2.list_transitions(target_states=(curstate2,))
    out_t1 = auto1.list_transitions(source_states=(curstate1,))
    out_t2 = auto2.list_transitions(source_states=(curstate2,))
    receiving1 = set(t[2] for t in in_t1)
    receiving2 = set(t[2] for t in in_t2)
    accepting1 = set(t[2] for t in out_t1)
    accepting2 = set(t[2] for t in out_t2)
    if not receiving1.issubset(receiving2):
        return False
    if not accepting1.issubset(accepting2):
        return False
    t1 = auto1.list_transitions(source_states=(curstate1,))
    t2 = auto2.list_transitions(source_states=(curstate2,))
    s1 = organize_transitions_by_symbols(t1)
    s2 = organize_transitions_by_symbols(t2)
    for sym in s1:
        newstate1 = s1[sym].pop()[1]
        newstate2 = s2[sym].pop()[1]
        assert len(s1[sym]) == 0
        assert len(s2[sym]) == 0
        if newstate1 not in visited:
            if not _is_subautomaton(auto1, auto2, newstate1, newstate2, visited):
                return False
    return True


def is_subautomaton(auto1, auto2):
    if not isinstance(auto1, Automaton) or not isinstance(auto2, Automaton):
        raise TypeError('please provide two instances of class Automaton')
    auto1 = convert_NFA_to_DFA(auto1, minimize=True)
    auto2 = convert_NFA_to_DFA(auto2, minimize=True)
    curstate1 = auto1.get_initial_state()
    curstate2 = auto2.get_initial_state()
    return _is_subautomaton(auto1, auto2, curstate1, curstate2)
