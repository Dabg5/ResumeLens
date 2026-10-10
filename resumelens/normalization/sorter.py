"""Profile-driven canonical sorting of normalized qualifications.

Between normalization and automata recognition, qualifications are sorted
into the canonical category order defined by each target professional profile.
Any qualification not required by the profile is preserved in `ignored` rather
than silently discarded, allowing transparent reporting in the UI.
"""
from collections.abc import Iterable
from dataclasses import dataclass

from resumelens.profiles import PROFILES, Profile


@dataclass(frozen=True)
class SortedQualifications:
    """Qualifications sorted according to a profile's category sequence."""
    profile_key: str
    sequence: tuple[str, ...]
    ignored: tuple[str, ...]


def sort_for_profile(canonicals: Iterable[str], profile: Profile) -> SortedQualifications:
    """Sort qualifications by (category_index, original_position) for `profile`.

    Duplicates are removed preserving the first occurrence.
    Qualifications not belonging to `profile` are routed to `ignored`.
    """
    seen: set[str] = set()
    accepted_items: list[tuple[int, int, str]] = []
    ignored_items: list[str] = []

    for pos, skill in enumerate(canonicals):
        if skill in seen:
            continue
        seen.add(skill)

        cat_idx = profile.category_index(skill)
        if cat_idx is not None:
            accepted_items.append((cat_idx, pos, skill))
        else:
            ignored_items.append(skill)

    accepted_items.sort(key=lambda item: (item[0], item[1]))
    sequence = tuple(item[2] for item in accepted_items)
    ignored = tuple(ignored_items)

    return SortedQualifications(
        profile_key=profile.key,
        sequence=sequence,
        ignored=ignored,
    )


def sort_for_all(canonicals: Iterable[str]) -> dict[str, SortedQualifications]:
    """Sort qualifications for all configured profiles."""
    return {
        key: sort_for_profile(canonicals, profile)
        for key, profile in PROFILES.items()
    }
