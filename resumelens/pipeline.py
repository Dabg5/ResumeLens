"""End-to-end résumé processing from plain text to classified candidate DSL."""
import re
from dataclasses import dataclass

from resumelens.dsl.renderer import to_html, to_markdown
from resumelens.dsl.serializer import CandidateData, ProfileVerdict, to_dsl
from resumelens.dsl.validator import ValidationReport, validate
from resumelens.extraction.extractor import ExtractionResult, extract
from resumelens.normalization.sorter import SortedQualifications, sort_for_all
from resumelens.normalization.transducers import GROUPED_CANONICALS, Normalization, normalize_all
from resumelens.profiles import PROFILES
from resumelens.recognition.classifier import ProfileMatch, classify_all


@dataclass(frozen=True)
class PipelineResult:
    """All intermediate and rendered outputs produced for one résumé."""

    extraction: ExtractionResult
    normalized: tuple[Normalization, ...]
    sorted_by_profile: dict[str, SortedQualifications]
    matches: tuple[ProfileMatch, ...]
    candidate: CandidateData
    dsl: str
    validation: ValidationReport
    markdown: str
    html: str


def _years(values: list[str]) -> int | None:
    """Read the first integer from the first extracted experience phrase."""
    if not values:
        return None
    match = re.search(r"\d+", values[0])
    return int(match.group()) if match else None


def run(text: str) -> PipelineResult:
    """Extract, normalize, sort, classify, serialize, validate and render text."""
    extracted = extract(text)
    normalized = tuple(normalize_all(extracted.skills))
    canonicals = tuple(item.canonical for item in normalized if item.canonical)
    sorted_by_profile = sort_for_all(canonicals)
    sequences = {key: value.sequence for key, value in sorted_by_profile.items()}
    matches = classify_all(sequences)

    category_by_skill = {
        skill: group for group, skills in GROUPED_CANONICALS.items() for skill in skills
    }
    skill_groups: dict[str, list[str]] = {}
    for canonical in dict.fromkeys(canonicals):
        group = category_by_skill.get(canonical)
        if group:
            skill_groups.setdefault(group, []).append(canonical)

    institutions = extracted.institutions
    education = tuple(
        (degree, institutions[index] if index < len(institutions) else None)
        for index, degree in enumerate(extracted.degrees)
    )
    candidate = CandidateData(
        name=extracted.name,
        emails=tuple(extracted.emails), phones=tuple(extracted.phones),
        urls=tuple(extracted.urls), years=_years(extracted.years_of_experience),
        periods=tuple(extracted.date_ranges), education=education,
        skills={key: tuple(value) for key, value in skill_groups.items()},
        verdicts=tuple(ProfileVerdict(
            profile_key=match.profile_key, accepted=match.accepted,
            sequence=match.sequence, missing=match.missing_categories,
        ) for match in matches),
    )
    source = to_dsl(candidate)
    report = validate(source)
    markdown = to_markdown(report.model) if report.valid else ""
    html = to_html(report.model) if report.valid else ""
    # The textX model is generated dynamically and is not needed by UI callers;
    # omit it from the cacheable result while retaining its validation outcome.
    cacheable_report = ValidationReport(report.valid, report.errors)
    return PipelineResult(extracted, normalized, sorted_by_profile, matches,
                          candidate, source, cacheable_report, markdown, html)
