"""Syntax and semantic validation for ResumeLens candidate DSL documents."""
from dataclasses import dataclass
from pathlib import Path

from textx import TextXSyntaxError, metamodel_from_file

from resumelens.normalization.aliases import ALIASES
from resumelens.profiles import PROFILES


@dataclass(frozen=True)
class ValidationReport:
    """Outcome of parsing and checking a candidate DSL source."""

    valid: bool
    errors: tuple[str, ...]
    model: object | None = None


_GRAMMAR = Path(__file__).with_name("candidate.tx")


def _syntax_error(error: TextXSyntaxError) -> str:
    return f"line {error.line}, col {error.col}: {error.message}"


def _semantic_errors(model: object) -> list[str]:
    errors: list[str] = []
    categories: set[str] = set()
    for group in model.skills.groups:
        if group.category in categories:
            errors.append(f"repeated skill category: {group.category}")
        categories.add(group.category)
        for skill in group.skills:
            if skill not in ALIASES:
                errors.append(f"unknown canonical qualification: {skill}")

    for result in model.classification.results:
        if result.profile not in PROFILES:
            errors.append(f"unknown profile: {result.profile}")
            continue
        if result.verdict == "ACCEPTED" and not result.sequence:
            errors.append(f"accepted profile requires a sequence: {result.profile}")
        allowed = set(PROFILES[result.profile].all_skills())
        for skill in result.sequence:
            if skill not in allowed:
                errors.append(
                    f"qualification outside profile alphabet ({result.profile}): {skill}"
                )
    return errors


def validate(source: str) -> ValidationReport:
    """Parse source and return syntax/lexical or semantic validation errors."""
    try:
        model = metamodel_from_file(str(_GRAMMAR)).model_from_str(source)
    except TextXSyntaxError as error:
        return ValidationReport(False, (_syntax_error(error),))
    errors = tuple(_semantic_errors(model))
    return ValidationReport(not errors, errors, model)
