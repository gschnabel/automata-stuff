def duplicate_automaton_part(
        automaton, start_state, clone_state=None, state_map=None
):
    state_map = state_map if state_map is not None else dict()
    clone_state = automaton.create_state() if clone_state is None else clone_state
    state_map[start_state] = clone_state
    terminal_states = list()
    for outstate in automaton.outgoing[start_state]:
        if outstate in state_map:
            new_state = state_map[outstate]
        else:
            new_state = automaton.create_state()
        for inpsymb in automaton.outgoing[start_state][outstate]:
            automaton.add_transition(clone_state, new_state, inpsymb)
        if outstate not in state_map:
            _, new_terminal_states, _ = automaton.duplicate_automaton_part(
                outstate, new_state, state_map
            )
            terminal_states.append(new_terminal_states)
    if len(automaton.outgoing[start_state]) == 0:
        terminal_states = set((clone_state,))
    else:
        terminal_states = set((x for y in terminal_states for x in y))
    return clone_state, terminal_states, state_map


def __locate_union_symb(self, rex, pos=0):
    bracket_counter = 0
    while pos < len(rex) and bracket_counter >= 0:
        cursymb = rex[pos]
        if cursymb == '(':
            bracket_counter += 1
        elif cursymb == ')':
            bracket_counter -= 1
        elif cursymb == '|' and bracket_counter == 0:
            return pos
        pos += 1
    return None


def rex_to_nfa(self, rex, pos=0, start_state=None):
    start_state = self.create_state(start_state)
    cur_state = start_state
    while pos < len(rex) and rex[pos] != ')':
        cursymb = rex[pos]
        union_pos = self.__locate_union_symb(rex, pos)
        if union_pos is not None:
            left_temp_state = self.create_state()
            right_temp_state = self.create_state()
            self.add_transition(cur_state, left_temp_state, 'eps')
            self.add_transition(cur_state, right_temp_state, 'eps')
            left_pos, left_terminal_state = \
                self.rex_to_nfa(rex[:union_pos], pos, left_temp_state)
            right_pos, right_terminal_state = \
                self.rex_to_nfa(rex, union_pos+1, right_temp_state)
            terminal_state = self.create_state()
            self.add_transition(left_terminal_state, terminal_state, 'eps')
            self.add_transition(right_terminal_state, terminal_state, 'eps')
            pos = right_pos
            if rex[pos] == ')':
                pos -= 1
        # treat brackets
        elif cursymb == '(':
            temp_state = self.create_state()
            self.add_transition(cur_state, temp_state, 'eps')
            pos, terminal_state = self.rex_to_nfa(rex, pos+1, temp_state)
            if len(rex) == pos or rex[pos] != ')':
                raise IndexError('missing closing bracket')
        # treat regular symbol
        else:
            terminal_state = self.create_state()
            self.add_transition(cur_state, terminal_state, cursymb)
        # treat with ?,+,*
        rex_symb = rex[pos+1] if pos+1 < len(rex) else ''
        # perform an automaton duplication for `+`
        if rex_symb == '+':
            clone_state, new_terminal_states, _ = \
                self.duplicate_automaton_part(cur_state)
            self.add_transition(terminal_state, clone_state, 'eps')
            cur_state = clone_state
            if len(new_terminal_states) != 1:
                raise IndexError('expect exactly one terminal state here')
            terminal_state = new_terminal_states.pop()
        # create appropriate epsilon transitions
        if rex_symb in ('?', '+', '*'):
            self.add_transition(cur_state, terminal_state, 'eps')
            if rex_symb in ('+', '*'):
                self.add_transition(terminal_state, cur_state, 'eps')
            pos += 1
        pos += 1
        cur_state = terminal_state
    return pos, cur_state

def to_dfa(self, cur_state=None):
    if cur_state is None:
        cur_state = list((s for s in self.states if not self.incoming[s]))
        if len(cur_state) != 1:
            raise IndexError('could not identify start state')
        cur_state = start_state[0]

    visited_outstates = set()
    transitions_by_symbols = dict()
    outstates = tuple(self.outgoing[cur_state])
    for i in range(len(outstates)-1):
        outstate1 = outstates[i]
        for j in range(i+1, len(outstates)):
            outstate2 = outstates[j]
            # TODO
            pass
