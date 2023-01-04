from .automaton import Automaton


class DFA(Automaton):

    def __init__(self, auto=None):
        super().__init__(auto)
        self._DFA_delta_table = None
        if auto is not None and not auto.is_DFA():
            raise TypeError('passed automaton does not qualify as DFA')

    def _build_DFA_transition_table(self):
        if not self.is_DFA():
            raise TypeError('cannot build a DFA transition table for an NFA')
        transitions = self.list_transitions()
        delta_table = dict()
        for curstate, outstate, sym in transitions:
            tmp = delta_table.setdefault(curstate, dict())
            tmp[sym] = outstate
        self._DFA_delta_table = delta_table

    def determine_target_state(self, state, symbol):
        if self._DFA_delta_table is None:
            self._build_DFA_transition_table()
        return self._DFA_delta_table[state].get(symbol, None)

    def is_valid_input(self, string):
        if not self.is_initial_state_defined():
            raise IndexError('initial state not defined')
        if not self.are_terminal_states_defined():
            raise IndexError('terminal states not defined')
        terminal_states = self.get_terminal_states()
        curstate = self.get_initial_state()
        pos = 0
        while pos < len(string):
            cursym = string[pos]
            next_state = self.determine_target_state(curstate, cursym)
            if next_state is None:
                return False
            pos += 1
            curstate = next_state
        return curstate in terminal_states

    def add_transition(self, source_state, target_state, input_symb):
        if (type(input_symb) == str and input_symb == 'eps' or
                type(input_symb) == set and 'eps' in input_symb):
            raise ValueError('epsilon transitions not allowed in DFA')
        transitions = self.list_transitions(source_states=(source_state,))
        if any((t[2] == input_symb for t in transitions)):
            raise ValueError(
                'multiple transitions from the same source state ' +
                'with the same input symbol are not allowed in a DFA'
            )
        self._DFA_delta_table = None
        ret = super().add_transition(source_state, target_state, input_symb)
        return ret

    def remove_transition(
        self, source_state, target_state, input_symb=None
    ):
        self._DFA_delta_table = None
        ret = super().remove_transition(source_state, target_state, input_symb)
        return ret

    def create_state(self, new_state=None):
        self._DFA_delta_table = None
        return super().create_state(new_state)

    def remove_state(self, state):
        self._DFA_delta_table = None
        return super().remove_state(state)
