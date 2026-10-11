"""Profile classification and human-readable recognition traces."""
from dataclasses import dataclass
from collections.abc import Iterable

from resumelens.profiles import PROFILES
from .automata import AutomatonTuple, automata, simulate


@dataclass(frozen=True)
class ProfileMatch:
    """Recognition outcome for one profile and one canonical sequence."""

    profile_key: str
    profile_name: str
    automaton_type: str
    sequence: tuple[str, ...]
    accepted: bool
    trace: tuple[str, ...]
    missing_categories: tuple[str, ...]


def _trace(t: AutomatonTuple, sequence: tuple[str, ...]) -> tuple[str, ...]:
    """Describe the path taken through category states."""
    outgoing: dict[str, list[tuple[str, str]]] = {}
    for source, symbol, target in t.transitions:
        outgoing.setdefault(source, []).append((symbol, target))
    state = t.start_state
    steps = [state]
    for symbol in sequence:
        queue = [(state, [])]
        visited = {state}
        found = None
        while queue and found is None:
            current, eps_path = queue.pop(0)
            for edge, target in outgoing.get(current, ()):
                if edge == symbol:
                    found = (target, eps_path)
                    break
                if edge == "ε" and target not in visited:
                    visited.add(target)
                    queue.append((target, eps_path + [target]))
        if found is None:
            steps.append(f"{state} -{symbol}-> ∅")
            break
        state, eps_path = found
        steps.extend(f"{epsilon_state} (ε)" for epsilon_state in eps_path)
        steps.append(f"{state} ({symbol})")
    return tuple(steps)


def classify(profile_key: str, sequence: Iterable[str]) -> ProfileMatch:
    """Check whether a canonical qualification sequence fits one profile."""
    if profile_key not in PROFILES:
        raise KeyError(f"unknown profile: {profile_key}")
    qualifications = tuple(sequence)
    profile = PROFILES[profile_key]
    _, tuple_view = automata()[profile_key]
    present = set(qualifications)
    missing = tuple(category.name for category in profile.categories
                    if not category.optional and not present.intersection(category.skills))
    return ProfileMatch(
        profile_key=profile.key,
        profile_name=profile.name,
        automaton_type=profile.automaton_type,
        sequence=qualifications,
        accepted=simulate(tuple_view, qualifications),
        trace=_trace(tuple_view, qualifications),
        missing_categories=missing,
    )


def classify_all(sequences: dict[str, Iterable[str]]) -> tuple[ProfileMatch, ...]:
    """Classify each configured profile using its own sorted sequence."""
    return tuple(classify(key, sequences.get(key, ())) for key in PROFILES)


def accepted_profiles(matches: Iterable[ProfileMatch]) -> tuple[ProfileMatch, ...]:
    """Return all accepted profiles in declaration order, without ranking."""
    by_key = {match.profile_key: match for match in matches if match.accepted}
    return tuple(by_key[key] for key in PROFILES if key in by_key)
