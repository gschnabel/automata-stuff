import re
import matplotlib.pyplot as plt
import networkx as nx


class Automaton():

    def __init__(self):
        self.incoming = dict()
        self.outgoing = dict()
        self.state_count = 0

    def add_transition(self, source_state, target_state, input_symb):
        if type(input_symb) == set and len(input_symb) == 0:
            return
        source_state = self.create_state(source_state)
        target_state = self.create_state(target_state)
        outdict = self.outgoing.setdefault(source_state, dict())
        outdict = outdict.setdefault(target_state, set())
        indict = self.incoming.setdefault(target_state, dict())
        indict[source_state] = outdict
        if type(input_symb) == str:
            outdict.add(input_symb)
        elif type(input_symb) == set:
            outdict.update(input_symb)
        else:
            raise TypeError('input_symb must be str or set')

    def remove_transition(
        self, source_state, target_state, input_symb=None
    ):
        if input_symb is None:
            del self.outgoing[source_state][target_state]
            del self.incoming[target_state][source_state]
            return None
        if type(input_symb) == set:
            self.outgoing[source_state][target_state] -= input_symb
        elif type(input_symb) == str:
            self.outgoing[source_state][target_state].remove(input_symb)
        else:
            raise TypeError('input_symb must be str or set')
        if not self.outgoing[source_state][target_state]:
            del self.outgoing[source_state][target_state]
            del self.incoming[target_state][source_state]

    def create_state(self, new_state=None):
        if new_state is None:
            new_state = self.state_count
        if new_state not in self.incoming:
            self.incoming[new_state] = dict()
            self.outgoing[new_state] = dict()
            if new_state >= self.state_count:
                self.state_count = new_state + 1
        return new_state

    def remove_state(self, state):
        if state not in self.outgoing:
            return False
        for outstate in self.outgoing[state]:
            del self.incoming[outstate][state]
        del self.outgoing[state]
        return True

    def list_states(self):
        return tuple(self.outgoing)

    def list_transitions(self):
        transitions = dict()
        for source_state, outdict in self.outgoing.items():
            for target_state, input_symbols in outdict.items():
                transitions[(source_state, target_state)] = \
                    input_symbols.copy()
        return transitions

    def list_terminal_states(self):
        return set((s for s, cset in self.outgoing.items() if not cset))

    def duplicate_automaton_part(
            self, start_state, clone_state=None, state_map=None
    ):
        state_map = state_map if state_map is not None else dict()
        clone_state = self.create_state() if clone_state is None else clone_state
        state_map[start_state] = clone_state
        terminal_states = list()
        for outstate in self.outgoing[start_state]:
            if outstate in state_map:
                new_state = state_map[outstate]
            else:
                new_state = self.create_state()
            for inpsymb in self.outgoing[start_state][outstate]:
                self.add_transition(clone_state, new_state, inpsymb)
            if outstate not in state_map:
                _, new_terminal_states, _ = self.duplicate_automaton_part(
                    outstate, new_state, state_map
                )
                terminal_states.append(new_terminal_states)
        if len(self.outgoing[start_state]) == 0:
            terminal_states = set((clone_state,))
        else:
            terminal_states = set((x for y in terminal_states for x in y))
        return clone_state, terminal_states, state_map

    def merge_states(self, state1, state2):
        if len(self.outgoing[state1]) > 0:
            tmp = state1
            state1 = state2
            state2 = tmp
        if (len(self.outgoing[state1]) > 0 or len(self.incoming[state2]) > 0):
            raise IndexError('one state must have only incoming links ' +
                             'and the other state only outgoing links')
        for outstate in tuple(self.outgoing[state2]):
            self.incoming[outstate][state1] = self.incoming[outstate][state2]
            self.outgoing[state1][outstate] = self.incoming[outstate][state1]
            del self.incoming[outstate][state2]
        self.remove_state(state2)
        return state1

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

    def determine_eps_substitution(self, state, visited_states=None):
        if visited_states is None:
            visited_states = set()
        visited_states.add(state)
        outstates = tuple(
            s for s, cset in self.outgoing[state].items()
            if 'eps' in cset
        )
        subst_states = dict()
        for outstate in outstates:
            for outstate2, syms in self.outgoing[outstate].items():
                if outstate2 in visited_states:
                    continue
                syms = syms.copy()
                upd_syms = subst_states.setdefault(outstate2, set())
                if 'eps' in syms:
                    syms.remove('eps')
                    subst_states2 = self.determine_eps_substitution(
                        outstate2, visited_states)
                    for s, t in subst_states2.items():
                        upd_syms2 = subst_states.setdefault(s, set())
                        upd_syms2.update(t)
                upd_syms.update(syms)
        return subst_states

    def remove_eps_transitions(self):
        for state in self.outgoing:
            subst_states = self.determine_eps_substitution(state)
            for s, t in tuple(subst_states.items()):
                self.add_transition(state, s, t)
        for s1, t1 in tuple(self.outgoing.items()):
            for s2, t2 in tuple(t1.items()):
                if 'eps' in t2:
                    self.remove_transition(s1, s2, 'eps')

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
