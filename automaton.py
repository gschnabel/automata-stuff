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

    def list_transitions(
        self, source_states=None, target_states=None, symbols=None
    ):
        if source_states is None:
            source_states = set(self.outgoing.keys())
        if target_states is None:
            target_states = set(self.outgoing.keys())
        transitions = set()
        for source_state in source_states:
            outdict = self.outgoing[source_state]
            for target_state, input_symbols in outdict.items():
                if target_state not in target_states:
                    continue
                if symbols is None:
                    allowed_symbols = input_symbols
                else:
                    allowed_symbols = input_symbols.intersection(symbols)
                for sym in allowed_symbols:
                    curtrans = (source_state, target_state, sym)
                    transitions.add(curtrans)
        return transitions
