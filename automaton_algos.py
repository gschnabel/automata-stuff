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


def rex_to_nfa(automaton, rex, pos=0, cur_state=None):
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
            left_pos, left_terminal_state = \
                rex_to_nfa(automaton, rex[:union_pos], pos, left_temp_state)
            right_pos, right_terminal_state = \
                rex_to_nfa(automaton, rex, union_pos+1, right_temp_state)
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
            pos, terminal_state = rex_to_nfa(automaton, rex, pos+1, temp_state)
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
        return set()
    visited.add(state)
    all_transitions = auto.list_transitions(source_states=(state,))
    eps_transitions = set((t for t in all_transitions if t[2] == 'eps'))
    new_transitions = set((t for t in all_transitions if t[2] != 'eps'))
    for transition in eps_transitions:
        outstate = transition[1]
        new_transitions.update(determine_transitions(auto, outstate, visited))
    return new_transitions


def clone_automaton_without_eps_transitions(original_automaton):
    auto = original_automaton
    clone_auto = Automaton()
    state_map = dict()
    # create new states for each nfa state
    states = auto.list_states()
    for s in states:
        new_state = clone_auto.create_state()
        state_map[s] = new_state
    # set initial and terminal states
    orig_initial_state = auto.get_initial_state()
    clone_auto.set_initial_state(state_map[orig_initial_state])
    orig_terminal_states = auto.get_terminal_states()
    for t in orig_terminal_states:
        clone_auto.add_terminal_state(state_map[t])
    # add transitions
    for state in states:
        curtransitions = determine_transitions(auto, state)
        new_source_state = state_map[state]
        for _, target_state, sym in curtransitions:
            new_target_state = state_map[target_state]
            clone_auto.add_transition(new_source_state, new_target_state, sym)
    # remove unreachable states
    unreachable = clone_auto.determine_unreachable_states()
    for s in unreachable:
        clone_auto.remove_state(s)
    return clone_auto
