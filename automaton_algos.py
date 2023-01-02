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


def rex_to_nfa(automaton, rex, pos=0, start_state=None):
    start_state = automaton.create_state(start_state)
    cur_state = start_state
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
    return pos, cur_state
