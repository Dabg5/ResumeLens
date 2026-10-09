"""Declarative definition of a professional profile.

A profile is an ordered sequence of categories. Each category holds the
canonical qualifications that can satisfy it. The same structure drives the
canonical sorting (stage 2) and the pattern automaton (stage 3).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    name: str
    skills: tuple[str, ...]
    optional: bool = False


@dataclass(frozen=True)
class Profile:
    key: str
    name: str
    description: str
    automaton_type: str  # "DFA", "NFA" or "ε-NFA"; justified in docs/02-formalization.md
    categories: tuple[Category, ...]

    def all_skills(self) -> tuple[str, ...]:
        return tuple(s for c in self.categories for s in c.skills)

    def category_index(self, skill: str) -> int | None:
        """Position of the category that contains `skill`, or None if the
        qualification is not part of this profile."""
        for i, category in enumerate(self.categories):
            if skill in category.skills:
                return i
        return None

    def canonical_order(self) -> tuple[str, ...]:
        """Every qualification of the profile in canonical order."""
        return self.all_skills()
