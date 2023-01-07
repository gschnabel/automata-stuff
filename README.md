# Automata stuff

This Python packages contains a class `Automaton`, which implements methods
for constructing and manipulating a [finite state automaton][finite-state-machine].
It also implements a class `DFA`, which specializes the `Automaton` class
to [deterministic finite automata][dfa-info] (DFA).

Additional functions are implemented to construct finite automata from regular
expressions, convert non-deterministic finite automata (NFA) to DFA and to
minimize the number of states in a DFA.

Finally---and this was the initial motivation to create this package--
it can be checked whether an automaton is a subautomaton of another one.
Due to the relationship between automata and regular expressions, it can
therefore be checked whether a given regular expression matches
a subset of the strings matched by another regular expression.
Please note that only basic features of regular expressions are implemented,
which are `.`, `*`, `+`, `?`, `|` and brackets but advanced features such as
character classes and named capture groups are not implemented.

## Installation

It may be easiest to download this repository and make the path available
via the `PYTHONPATH` environment variable. Alternatively, the package
can be installed via pip by
```
pip install git+https://github.com/gschnabel/automata-stuff.git
```
or if the repository folder has already been downloaded by
```
pip install <local repository folder>
```
At least under Linux, it seems to be necessary to prefix relative paths
by `./`.

## Usage

The `examples/` directory contains a couple of scripts that showcase
some of the available functions.

## License

This package is provided under [The Unlicense][the-unlicense] license,
which essentially means that the code is released into the public domain.
Consult the accompanying `LICENSE` file for the full details of this license. 

[finite-state-machine]: https://en.wikipedia.org/wiki/Finite-state_machine 
[dfa-info]: https://en.wikipedia.org/wiki/Deterministic_finite_automaton
[the-unlicense]: https://unlicense.org/



