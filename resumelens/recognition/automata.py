"""Finite automata generated from ordered professional profile categories."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton as DFA,
    Epsilon,
    EpsilonNFA,
)

from resumelens.profiles import PROFILES, Profile


@dataclass(frozen=True)
class AutomatonTuple:
    """Inspectable five-tuple representation of a profile automaton."""

    name: str
    states: tuple[str, ...]
    alphabet: tuple[str, ...]
    transitions: tuple[tuple[str, str, str], ...]
    start_state: str
    final_states: tuple[str, ...]
    kind: str
    pattern: str = ""

    def edges(self) -> tuple[tuple[str, str, str], ...]:
        """Return transitions as (source, label, target) edges."""
        return self.transitions

    def as_markdown(self) -> str:
        """Render the automaton's formal five-tuple as Markdown."""
        rows = [
            f"### {self.name} ({self.kind})", "",
            f"- **Q:** {{{', '.join(self.states)}}}",
            f"- **Σ:** {{{', '.join(self.alphabet)}}}",
            f"- **δ:** {len(self.transitions)} transitions",
            f"- **q₀:** {self.start_state}",
            f"- **F:** {{{', '.join(self.final_states)}}}", "",
            "| State | Symbol | Next state |", "|---|---|---|",
        ]
        rows.extend(f"| {src} | {label} | {dst} |" for src, label, dst in self.transitions)
        return "\n".join(rows)

    def regex(self) -> str:
        """Return the category-order pattern, marking optional categories."""
        return self.pattern


def _category_regex(profile: Profile) -> str:
    return " ".join(
        f"({' | '.join(category.skills)}){'*' if category.optional else '+'}"
        for category in profile.categories
    )


def build_automaton(profile: Profile) -> tuple[object, AutomatonTuple]:
    """Build a DFA or epsilon-NFA and its displayable five-tuple."""
    states = tuple(f"q{i}" for i in range(len(profile.categories) + 1))
    transitions: list[tuple[str, str, str]] = []
    alphabet = tuple(profile.all_skills())
    epsilon_nfa = profile.automaton_type == "ε-NFA"
    automaton = EpsilonNFA() if epsilon_nfa else DFA()
    automaton.add_start_state(states[0])
    automaton.add_final_state(states[-1])

    for index, category in enumerate(profile.categories):
        source, target = states[index], states[index + 1]
        for skill in category.skills:
            automaton.add_transition(source, skill, target)
            automaton.add_transition(target, skill, target)
            transitions.append((source, skill, target))
            transitions.append((target, skill, target))
        if category.optional:
            automaton.add_transition(source, Epsilon(), target)
            transitions.append((source, "ε", target))

    tuple_view = AutomatonTuple(
        name=profile.name, states=states, alphabet=alphabet,
        transitions=tuple(transitions), start_state=states[0],
        final_states=(states[-1],), kind=profile.automaton_type,
        pattern=_category_regex(profile),
    )
    return automaton, tuple_view


def automata() -> dict[str, tuple[object, AutomatonTuple]]:
    """Build all profile automata in the declared profile order."""
    return {key: build_automaton(profile) for key, profile in PROFILES.items()}


def infer_kind(t: AutomatonTuple | Iterable[tuple[str, str, str]]) -> str:
    """Infer DFA, NFA or epsilon-NFA from a transition collection."""
    transitions = t.transitions if isinstance(t, AutomatonTuple) else tuple(t)
    destinations: dict[tuple[str, str], set[str]] = defaultdict(set)
    for source, symbol, target in transitions:
        if symbol in ("ε", "$", "epsilon"):
            return "ε-NFA"
        destinations[(source, symbol)].add(target)
    return "NFA" if any(len(targets) > 1 for targets in destinations.values()) else "DFA"


def simulate(t: AutomatonTuple, word: Iterable[str]) -> bool:
    """Run a sequence of canonical qualifications with epsilon closure."""
    epsilons = {"ε", "$", "epsilon"}
    outgoing: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for source, symbol, target in t.transitions:
        outgoing[source].append((symbol, target))

    def closure(states: set[str]) -> set[str]:
        result = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for symbol, target in outgoing[state]:
                if symbol in epsilons and target not in result:
                    result.add(target)
                    stack.append(target)
        return result

    current = closure({t.start_state})
    for symbol in word:
        current = closure({target for state in current
                           for edge, target in outgoing[state] if edge == symbol})
        if not current:
            return False
    return bool(current & set(t.final_states))
