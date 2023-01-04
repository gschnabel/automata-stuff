import copy
import string


class Automaton():

    def __init__(self, auto=None):
        self.incoming = dict()
        self.alphabet = set(string.printable)
        self.alphabet.add('eps')
        self.outgoing = dict()
        self.terminal_states = set()
        self.initial_state = None
        self.state_count = 0
        if auto is not None:
            if not isinstance(auto, Automaton):
                return TypeError('instance of Automaton class expected')
            for state in auto.list_states():
                self.create_state(state)
            for source_state, target_state, sym in auto.list_transitions():
                self.add_transition(source_state, target_state, sym)
            if auto.is_initial_state_defined():
                self.set_initial_state(auto.get_initial_state())
            if auto.are_terminal_states_defined():
                self.set_terminal_states(auto.get_terminal_states())

    def copy(self):
        return copy.deepcopy(self)

    def add_transition(self, source_state, target_state, input_symb):
        if type(input_symb) == set and len(input_symb) == 0:
            return
        if type(input_symb) == str and input_symb not in self.alphabet:
            raise ValueError(f'input symbol {input_symb} not in alphabet')
        elif type(input_symb) == set and input_symb.difference(self.alphabet):
            raise ValueError(
                f'some of the input symbols {input_symb} not in alphabet'
            )
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
        if self.is_initial_state(state):
            self.initial_state = None
        if self.is_terminal_state(state):
            self.terminal_states.remove(state)
        return True

    def set_symbols(self, symbols):
        self.alphabet = set(symbols)

    def add_symbol(self, symbol):
        self.alphabet.add(symbol)

    def list_symbols(self, only_used=False, include_eps=True):
        if not only_used:
            ret = self.alphabet.copy()
            if not include_eps:
                ret.remove('eps')
            return ret
        else:
            all_transitions = self.list_transitions()
            ret = set()
            for t in all_transitions:
                ret.add(t[2])
        if not include_eps:
            if 'eps' in ret:
                ret.remove('eps')
        return ret

    def get_eps_symbol(self):
        return 'eps'

    def list_states(self):
        return set(self.outgoing)

    def list_transitions(
        self, source_states=None, target_states=None, symbols=None,
        symbols_in_dict=False
    ):
        if source_states is None:
            source_states = set(self.outgoing.keys())
        if target_states is None:
            target_states = set(self.outgoing.keys())
        transitions = dict() if symbols_in_dict else set()
        for source_state in source_states:
            outdict = self.outgoing[source_state]
            for target_state, input_symbols in outdict.items():
                if target_state not in target_states:
                    continue
                if symbols is None:
                    allowed_symbols = input_symbols
                else:
                    allowed_symbols = input_symbols.intersection(symbols)
                    if len(allowed_symbols) == 0:
                        continue
                if symbols_in_dict:
                    curtrans = (source_state, target_state)
                    transitions[curtrans] = allowed_symbols
                else:
                    for sym in allowed_symbols:
                        curtrans = (source_state, target_state, sym)
                        transitions.add(curtrans)
        return transitions

    def has_no_incoming_transitions(self, state):
        return len(self.incoming[state]) == 0

    def has_no_outgoing_transitions(self, state):
        return len(self.outgoing[state]) == 0

    def _determine_reachable_states(self, start_state=None, reachable=None):
        if start_state is None:
            start_state = self.get_initial_state()
            if start_state is None:
                raise IndexError('no initial state defined')
        if reachable is None:
            reachable = set()
        elif start_state in reachable:
            return reachable
        reachable.add(start_state)
        transitions = self.list_transitions(
            source_states=(start_state,), symbols_in_dict=True
        )
        for source_state, target_state in transitions:
            self._determine_reachable_states(target_state, reachable)
        return reachable

    def determine_reachable_states(self, start_state=None):
        return self._determine_reachable_states(start_state)

    def determine_unreachable_states(self, start_state=None):
        reachable = self._determine_reachable_states(start_state)
        all_states = self.list_states()
        return all_states.difference(reachable)

    def set_terminal_states(self, states):
        if type(states) != set:
            raise TypeError('expecting a `set` of terminal states')
        existing_states = self.outgoing.keys()
        missing_states = [s for s in states if s not in existing_states]
        if len(missing_states) > 0:
            raise IndexError(f'these states do not exist: {missing_states}')
        self.terminal_states = states.copy()

    def add_terminal_state(self, state):
        if state not in self.outgoing:
            raise IndexError('the state {state} does not exist')
        self.terminal_states.add(state)

    def get_terminal_states(self):
        return self.terminal_states.copy()

    def is_terminal_state(self, state):
        return state in self.terminal_states

    def set_initial_state(self, state):
        if state not in self.outgoing:
            raise IndexError(f'the state {state} does not exist')
        self.initial_state = state

    def get_initial_state(self):
        return self.initial_state

    def is_initial_state(self, state):
        return state == self.initial_state

    def is_initial_state_defined(self):
        return self.initial_state is not None

    def are_terminal_states_defined(self):
        return len(self.terminal_states) > 0

    def contains_eps_transitions(self):
        symbols = self.list_symbols(only_used=True, include_eps=True)
        return 'eps' in symbols

    def is_DFA(self):
        if self.contains_eps_transitions():
            return False
        transitions = self.list_transitions()
        symdict = dict()
        for curstate, outstate, sym in transitions:
            key = (curstate, sym)
            symdict.setdefault(key, 0)
            symdict[key] += 1
            if symdict[key] > 1:
                return False
        return True
