from automaton import Automaton
from regex_utils import locate_union_symb


def duplicate_automaton_part(
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
            _, new_terminal_states, _ = duplicate_automaton_part(
                automaton, outstate, new_state, state_map
            )
            terminal_states.append(new_terminal_states)
    if len(automaton.outgoing[start_state]) == 0:
        terminal_states = set((clone_state,))
    else:
        terminal_states = set((x for y in terminal_states for x in y))
    return clone_state, terminal_states, state_map


def create_NFA_from_rex(automaton, rex, pos=0, cur_state=None):
    is_most_outer_call = cur_state is None
    cur_state = automaton.create_state(cur_state)
    if is_most_outer_call:
        automaton.set_initial_state(cur_state)
    while pos < len(rex) and rex[pos] != ')':
        cursymb = rex[pos]
        union_pos = locate_union_symb(rex, pos)
        if union_pos is not None:
            left_temp_state = automaton.create_state()
            right_temp_state = automaton.create_state()
            automaton.add_transition(cur_state, left_temp_state, 'eps')
            automaton.add_transition(cur_state, right_temp_state, 'eps')
            left_pos, left_terminal_state = create_NFA_from_rex(
                automaton, rex[:union_pos], pos, left_temp_state
            )
            right_pos, right_terminal_state = create_NFA_from_rex(
                automaton, rex, union_pos+1, right_temp_state
            )
            terminal_state = automaton.create_state()
            automaton.add_transition(left_terminal_state, terminal_state, 'eps')
            automaton.add_transition(right_terminal_state, terminal_state, 'eps')
            pos = right_pos
            if rex[pos] == ')':
                pos -= 1
        # treat brackets
        elif cursymb == '(':
            temp_state = automaton.create_state()
            automaton.add_transition(cur_state, temp_state, 'eps')
            pos, terminal_state = create_NFA_from_rex(
                automaton, rex, pos+1, temp_state
            )
            if len(rex) == pos or rex[pos] != ')':
                raise IndexError('missing closing bracket')
        # treat regular symbol
        else:
            terminal_state = automaton.create_state()
            automaton.add_transition(cur_state, terminal_state, cursymb)
        # treat with ?,+,*
        rex_symb = rex[pos+1] if pos+1 < len(rex) else ''
        # perform an automaton duplication for `+`
        if rex_symb == '+':
            clone_state, new_terminal_states, _ = \
                duplicate_automaton_part(automaton, cur_state)
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
        pos += 1
        cur_state = terminal_state
        if is_most_outer_call:
            automaton.set_terminal_states(set((cur_state,)))
    return pos, cur_state


def determine_transitions(auto, state, visited=None):
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
            determine_transitions(auto, outstate, visited)
        new_transitions.update(inherited_transitions)
        if inherited_terminal_state_flag:
            terminal_state_flag = True
    return new_transitions, terminal_state_flag


def convert_NFA_to_NFA_without_eps(original_automaton):
    auto = original_automaton
    clone_auto = Automaton()
    state_map = dict()
    # create new states for each nfa state
    states = auto.list_states()
    for s in states:
        new_state = clone_auto.create_state()
        state_map[s] = new_state
    # set initial state of new nfa
    original_initial_state = auto.get_initial_state()
    new_initial_state = state_map[original_initial_state]
    clone_auto.set_initial_state(new_initial_state)
    # add transitions
    for state in states:
        curtransitions, is_terminal_state = determine_transitions(auto, state)
        new_source_state = state_map[state]
        if is_terminal_state:
            clone_auto.add_terminal_state(new_source_state)
        for _, target_state, sym in curtransitions:
            new_target_state = state_map[target_state]
            clone_auto.add_transition(new_source_state, new_target_state, sym)
    # remove unreachable states
    unreachable = clone_auto.determine_unreachable_states()
    for s in unreachable:
        clone_auto.remove_state(s)
    return clone_auto


def convert_NFA_without_eps_to_DFA(original_automaton):
    auto = original_automaton
    clone_auto = auto.copy()
    untreated_states = clone_auto.list_states()
    while len(untreated_states) > 0:
        s = untreated_states.pop()
        transitions = clone_auto.list_transitions(source_states=(s,))
        sym_dict = dict()
        for t in transitions:
            cursym = t[2]
            curtransitions = sym_dict.setdefault(cursym, set())
            curtransitions.add(t)
        for sym, ts in sym_dict.items():
            if len(ts) == 1:
                continue
            new_state = clone_auto.create_state()
            untreated_states.add(new_state)
            is_terminal_state = any(
                (auto.is_terminal_state(tt[1]) for tt in ts)
            )
            if is_terminal_state:
                clone_auto.add_terminal_state(new_state)
            clone_auto.add_transition(s, new_state, sym)
            orig_target_states = {t[1] for t in ts}
            new_transitions = auto.list_transitions(
                source_states=orig_target_states
            )
            for _, new_target_state, new_sym in new_transitions:
                clone_auto.add_transition(
                    new_state, new_target_state, new_sym
                )
            for t in ts:
                clone_auto.remove_transition(t[0], t[1], t[2])
    # remove unreachable states
    unreachable = clone_auto.determine_unreachable_states()
    for s in unreachable:
        clone_auto.remove_state(s)
    return clone_auto


def convert_DFA_to_minimal_DFA(original_automaton):
    auto = original_automaton
    new_auto = auto.copy()
    all_states = new_auto.list_states()
    partitions = {i: set((s,)) for i, s in enumerate(all_states)}
    partitions_changed = True
    while partitions_changed:
        partitions_changed = False
        treated_partitions = dict()
        while len(partitions) > 0:
            partition_index, curpartition = partitions.popitem()
            treated_partitions[partition_index] = curpartition
            curstate = curpartition.pop()
            curpartition.add(curstate)
            curts = new_auto.list_transitions(source_states=(curstate,))
            curts = {(t[1], t[2]) for t in curts}
            is_cur_terminal = new_auto.is_terminal_state(curstate)
            for test_index, testpartition in tuple(partitions.items()):
                teststate = testpartition.pop()
                testpartition.add(teststate)
                testts = new_auto.list_transitions(source_states=(teststate,))
                testts = {(t[1], t[2]) for t in testts}
                is_test_terminal = new_auto.is_terminal_state(teststate)
                if (curts == testts and is_cur_terminal == is_test_terminal):
                    curpartition.update(testpartition)
                    del partitions[test_index]
                    partitions_changed = True
        # now we are merging equivalent states together
        # and adjust the transitions of other states to point to the new ones
        for idx, p in treated_partitions.items():
            if len(p) == 1:
                partitions[idx] = p
                continue
            curts = new_auto.list_transitions(target_states=p)
            new_state = new_auto.create_state()
            for curstate in p:
                new_auto.remove_state(curstate)
            for source_state, target_state, sym in curts:
                new_auto.add_transition(source_state, new_state, sym)
            partitions[idx] = set((new_state,))
    return new_auto
