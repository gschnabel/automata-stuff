from ..automaton import Automaton
from ..DFA import DFA
from ..utils.regex_utils import (
    locate_union_symb,
    remove_caret_and_dollar,
    expand_plus
)


def _duplicate_automaton_part(
        automaton, start_state, clone_state=None, state_map=None
):
    state_map = state_map if state_map is not None else dict()
    clone_state = automaton.create_state() if clone_state is None else clone_state
    state_map[start_state] = clone_state
    terminal_states = list()
    out_transitions = automaton.list_transitions(source_states=(start_state,))
    for _, outstate, inpsym in out_transitions:
        if outstate in state_map:
            new_state = state_map[outstate]
        else:
            new_state = automaton.create_state()
        automaton.add_transition(clone_state, new_state, inpsym)
        if outstate not in state_map:
            _, new_terminal_states, _ = _duplicate_automaton_part(
                automaton, outstate, new_state, state_map
            )
            terminal_states.append(new_terminal_states)
    if len(automaton.outgoing[start_state]) == 0:
        terminal_states = set((clone_state,))
    else:
        terminal_states = set((x for y in terminal_states for x in y))
    return clone_state, terminal_states, state_map


def _deal_with_rex_modifiers(automaton, rex, pos, cur_state, terminal_state):
    # treat with ?,+,*
    rex_symb = rex[pos] if pos < len(rex) else ''
    # perform an automaton duplication for `+`
    if rex_symb == '+':
        clone_state, new_terminal_states, _ = \
            _duplicate_automaton_part(automaton, cur_state)
        automaton.add_transition(terminal_state, clone_state, 'eps')
        cur_state = clone_state
        if len(new_terminal_states) != 1:
            raise IndexError('expect exactly one terminal state here')
        terminal_state = new_terminal_states.pop()
    # create appropriate epsilon transitions
    if rex_symb in ('?', '+', '*'):
        automaton.add_transition(cur_state, terminal_state, 'eps')
        if rex_symb in ('+', '*'):
            automaton.add_transition(terminal_state, cur_state, 'eps')
        pos += 1
    return pos, terminal_state


def _deal_with_union_rex(automaton, rex, pos, cur_state):
    union_pos = locate_union_symb(rex, pos)
    if union_pos is None:
        return pos, cur_state
    left_temp_state = automaton.create_state()
    right_temp_state = automaton.create_state()
    automaton.add_transition(cur_state, left_temp_state, 'eps')
    automaton.add_transition(cur_state, right_temp_state, 'eps')
    left_pos, left_terminal_state = _create_NFA_from_rex(
        automaton, rex[:union_pos], pos, left_temp_state
    )
    right_pos, right_terminal_state = _create_NFA_from_rex(
        automaton, rex, union_pos+1, right_temp_state
    )
    terminal_state = automaton.create_state()
    automaton.add_transition(left_terminal_state, terminal_state, 'eps')
    automaton.add_transition(right_terminal_state, terminal_state, 'eps')
    pos = right_pos
    return pos, terminal_state


def _deal_with_bracketed_rex(automaton, rex, pos, cur_state):
    if rex[pos] != '(':
        return pos, cur_state
    temp_state = automaton.create_state()
    automaton.add_transition(cur_state, temp_state, 'eps')
    pos, terminal_state = _create_NFA_from_rex(
        automaton, rex, pos+1, temp_state
    )
    if len(rex) == pos or rex[pos] != ')':
        raise IndexError('missing closing bracket')
    pos += 1
    return pos, terminal_state


def _deal_with_dot(automaton, rex, pos, cur_state):
    if rex[pos] != '.':
        return pos, cur_state
    temp_state = automaton.create_state()
    automaton.add_transition(cur_state, temp_state, 'eps')
    temp_state2 = automaton.create_state()
    symbols = automaton.list_symbols(include_eps=False)
    assert 'eps' not in symbols
    automaton.add_transition(temp_state, temp_state2, symbols)
    terminal_state = automaton.create_state()
    automaton.add_transition(temp_state2, terminal_state, 'eps')
    pos += 1
    return pos, terminal_state


def _deal_with_symbol(automaton, rex, pos, cur_state):
    cursymb = rex[pos]
    if cursymb == '\\':
        pos += 1
        cursymb = rex[pos]
    terminal_state = automaton.create_state()
    automaton.add_transition(cur_state, terminal_state, cursymb)
    pos += 1
    return pos, terminal_state


def _create_NFA_from_rex(automaton, rex, pos=0, cur_state=None):
    specialised_dealers = tuple((
        _deal_with_union_rex,
        _deal_with_bracketed_rex,
        _deal_with_dot,
        _deal_with_symbol
    ))
    while pos < len(rex) and rex[pos] != ')':
        for current_dealer in specialised_dealers:
            new_pos, terminal_state = current_dealer(
                automaton, rex, pos, cur_state
            )
            if pos != new_pos:
                pos, terminal_state = _deal_with_rex_modifiers(
                    automaton, rex, new_pos, cur_state, terminal_state
                )
                break
        cur_state = terminal_state
    return pos, cur_state


def create_NFA_from_rex(rex):
    auto = Automaton()
    rex = remove_caret_and_dollar(rex)
    rex = expand_plus(rex)
    initial_state = auto.create_state()
    auto.set_initial_state(initial_state)
    pos, terminal_state = _create_NFA_from_rex(auto, rex, 0, initial_state)
    auto.set_terminal_states(set((terminal_state,)))
    return auto


def _determine_transitions(auto, state, visited=None):
    if visited is None:
        visited = set()
    elif state in visited:
        return (set(), False)
    visited.add(state)
    all_transitions = auto.list_transitions(source_states=(state,))
    eps_transitions = set((t for t in all_transitions if t[2] == 'eps'))
    new_transitions = set((t for t in all_transitions if t[2] != 'eps'))
    terminal_state_flag = auto.is_terminal_state(state)
    for transition in eps_transitions:
        outstate = transition[1]
        inherited_transitions, inherited_terminal_state_flag = \
            _determine_transitions(auto, outstate, visited)
        new_transitions.update(inherited_transitions)
        if inherited_terminal_state_flag:
            terminal_state_flag = True
    return new_transitions, terminal_state_flag


def convert_NFA_to_NFA_without_eps(original_automaton):
    auto = original_automaton
    clone_auto = Automaton()
    state_map = dict()
    # set initial state of new nfa
    original_initial_state = auto.get_initial_state()
    new_initial_state = clone_auto.create_state()
    state_map[original_initial_state] = new_initial_state
    clone_auto.set_initial_state(new_initial_state)
    untreated_states = set((original_initial_state,))
    # add transitions
    while len(untreated_states) > 0:
        state = untreated_states.pop()
        new_state = state_map[state]
        curtransitions, is_terminal_state = _determine_transitions(auto, state)
        if is_terminal_state:
            clone_auto.add_terminal_state(new_state)
        for _, target_state, sym in curtransitions:
            if target_state not in state_map:
                new_target_state = clone_auto.create_state()
                state_map[target_state] = new_target_state
                untreated_states.add(target_state)
            new_target_state = state_map[target_state]
            clone_auto.add_transition(new_state, new_target_state, sym)
    return clone_auto


def _organize_transitions_by_symbols(transitions):
    sym_dict = dict()
    for t in transitions:
        cursym = t[2]
        curtransitions = sym_dict.setdefault(cursym, set())
        curtransitions.add(t)
    return sym_dict


def convert_NFA_without_eps_to_DFA(original_automaton):
    auto = original_automaton
    new_auto = Automaton()
    initial_state = auto.get_initial_state()
    new_initial_state = new_auto.create_state()
    new_auto.set_initial_state(new_initial_state)
    state_map = dict()
    state_map[(initial_state,)] = new_initial_state
    untreated_states = set()
    untreated_states.add((initial_state,))
    visited = set()
    while len(untreated_states) > 0:
        cur_state_tuple = untreated_states.pop()
        curstate = state_map[cur_state_tuple]
        visited.add(cur_state_tuple)
        transitions = auto.list_transitions(source_states=set(cur_state_tuple))
        ts_by_sym = _organize_transitions_by_symbols(transitions)
        for sym, ts in ts_by_sym.items():
            new_state_tuple = tuple(sorted(set(t[1] for t in ts)))
            if new_state_tuple not in state_map:
                new_state = new_auto.create_state()
                state_map[new_state_tuple] = new_state
                if new_state_tuple not in visited:
                    untreated_states.add(new_state_tuple)
                is_terminal_state = any(
                    (auto.is_terminal_state(tt[1]) for tt in ts)
                )
                if is_terminal_state:
                    new_auto.add_terminal_state(new_state)
            new_state = state_map[new_state_tuple]
            new_auto.add_transition(curstate, new_state, sym)
    return DFA(new_auto)


def convert_DFA_to_minimal_DFA(original_automaton):
    auto = original_automaton
    if not isinstance(auto, DFA):
        raise TypeError(
            'a DFA (deterministic finite automaton) is expected as input'
        )
    all_states = auto.list_states()
    terminal_states = auto.get_terminal_states()
    nonterminal_states = all_states.difference(terminal_states)
    # determine partitions corresponding to states of minimal DFA
    partitions = list((terminal_states, nonterminal_states))
    state_partition_map = dict()
    state_partition_map.update({s: 0 for s in terminal_states})
    state_partition_map.update({s: 1 for s in nonterminal_states})
    is_terminal_partition = [True, False]
    while True:
        partitions_changed = False
        for i, curpartition in enumerate(tuple(partitions)):
            untreated = curpartition.copy()
            new_partition = curpartition
            is_curpart_terminal = is_terminal_partition[i]
            while True:
                curstate = untreated.pop()
                curts = auto.list_transitions(source_states=(curstate,))
                curts = set((t[2], state_partition_map[t[1]]) for t in curts)
                disting = set()
                while len(untreated) > 0:
                    teststate = untreated.pop()
                    testts = auto.list_transitions(source_states=(teststate,))
                    testts = set((t[2], state_partition_map[t[1]]) for t in testts)
                    if curts != testts:
                        disting.add(teststate)
                if len(disting) == 0:
                    break
                partitions_changed = True
                new_partition.difference_update(disting)
                new_partition = disting
                partitions.append(new_partition)
                is_terminal_partition.append(is_curpart_terminal)
                untreated = new_partition.copy()
        # update the state_partition_map
        for i, p in enumerate(partitions):
            for s in p:
                state_partition_map[s] = i
        if not partitions_changed:
            break
    # construct the minimal DFA
    new_auto = Automaton()
    for i in range(len(partitions)):
        new_auto.create_state(i)
        if is_terminal_partition[i]:
            new_auto.add_terminal_state(i)
    for i, p in enumerate(partitions):
        orig_source_state = p.pop()
        p.add(orig_source_state)
        trans = auto.list_transitions(source_states=(orig_source_state,))
        trans = set((i, state_partition_map[t[1]], t[2]) for t in trans)
        for t in trans:
            new_auto.add_transition(t[0], t[1], t[2])
    orig_initial_state = auto.get_initial_state()
    new_auto.set_initial_state(state_partition_map[orig_initial_state])
    return DFA(new_auto)


def convert_NFA_to_DFA(automaton, minimize=True):
    auto = convert_NFA_to_NFA_without_eps(automaton)
    auto = convert_NFA_without_eps_to_DFA(auto)
    if minimize:
        auto = convert_DFA_to_minimal_DFA(auto)
    return auto


def create_DFA_from_rex(rex, minimize=True):
    auto = create_NFA_from_rex(rex)
    auto = convert_NFA_to_DFA(auto, minimize)
    return auto
