import re
import matplotlib.pyplot as plt
import networkx as nx

class Automaton():

    def __init__(self):
        self.states = set()
        self.transitions = dict()
        self.incoming = dict()
        self.outgoing = dict()
        self.state_count = 0

    def add_transition(self, source_state, target_state, input_symb):
        source_state = self.create_state(source_state)
        target_state = self.create_state(target_state)
        new_transition = (source_state, target_state)
        self.transitions.setdefault(new_transition, set())
        if type(input_symb) == str:
            self.transitions[new_transition].add(input_symb)
        elif hasattr(input_symb, '__iter__'):
            self.transitions[new_transition].update(input_symb)
        self.outgoing.setdefault(source_state, set())
        self.outgoing[source_state].add(target_state)
        self.incoming.setdefault(target_state, set())
        self.incoming[target_state].add(source_state)

    def remove_transition(
        self, source_state, target_state, input_symb, remove_isolated=False
    ):
        transition = (source_state, target_state)
        self.transitions[transition].remove(input_symb)
        if not self.transitions[transition]:
            del self.transitions[transition]
        self.outgoing[source_state].remove(target_state)
        self.incoming[target_state].remove(source_state)

    def create_state(self, new_state=None):
        if new_state is None:
            new_state = self.state_count
        if new_state not in self.states:
            self.states.add(new_state)
            self.incoming[new_state] = set()
            self.outgoing[new_state] = set()
            if new_state >= self.state_count:
                self.state_count = new_state + 1
        return new_state

    def remove_state(self, state):
        if state not in self.states:
            return False
        self.states.remove(state)
        for outstate in self.outgoing[state]:
            transition = (state, outstate)
            del self.transitions[transition]
        for instate in self.incoming[state]:
            transition = (instate, state)
            del self.transitions[transition]
        return True

    def list_states(self):
        return self.states.copy()

    def list_transitions(self):
        return set((t[0], t[1], s)
                   for t, tc in self.transitions.items()
                   for s in tc)

    def list_terminal_states(self):
        return set((s for s in self.states if not self.outgoing[s]))

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
            transition = (start_state, outstate)
            for inpsymb in self.transitions[transition]:
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
        for transition in tuple(self.transitions):
            if state2 not in transition:
                continue
            new_source_state = transition[0]
            new_target_state = transition[1]
            if new_source_state == state2:
                new_source_state = state1
            if new_target_state == state2:
                new_target_state = state1
            inp_symbs = self.transitions[transition]
            self.add_transition(new_source_state, new_target_state, inp_symbs)
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



auto = Automaton()

auto.add_transition(0, 3, 'a')
auto.add_transition(1, 3, 'b')
# auto.add_transition(3, 0, 'x')
auto.add_transition(0, 1, 'c')
auto.add_transition(0, 2, 'y')
auto.list_transitions()

auto.duplicate_automaton_part(0)
auto.list_transitions()
auto.merge_states(3, 4)

auto.to_dfa()

'abc(uvw|123)'
'(abc|(12)+3)'


special_rex = 'abcdef'
general_rex = 'abc(def|123)'

rex = 'a+b'
'aaaab', 'ab'
rex = 'a?b'
'b', 'ab'
rex = 'a*b'
'b', 'ab', 'aaaaab'
rex = 'abc(def|123)*xyz'
'abcxyz', 'abcdefxyz', 'abc123xyz', 'abcdef123123defdefxyz'
rex = 'the (the ?)+'
'the the', 'the the ', 'the thethe', 'the the thethethe the '





is_contained(special_rex, general_rex)






auto = Automaton()
auto.rex_to_nfa('(abc|(12)+3)')
edges = tuple(auto.transitions.keys())
G = nx.DiGraph()
G.add_edges_from(edges)
pos = nx.spring_layout(G)
plt.figure(figsize=(10, 10))
nx.draw(
    G, pos, edge_color='black', width=1, linewidths=1,
    node_size=500, node_color='pink', alpha=0.9,
    labels={node: node for node in G.nodes()},
)
nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=auto.transitions,
    font_color='red',
)
plt.axis('off')
plt.show()


