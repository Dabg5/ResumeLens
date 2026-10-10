"""Serialization of candidate information to the ResumeLens DSL."""
from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProfileVerdict:
    """Recognition result represented in a candidate document."""

    profile_key: str
    accepted: bool
    sequence: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateData:
    """Data needed to produce a self-contained candidate DSL document."""

    name: str | None = None
    emails: tuple[str, ...] = ()
    phones: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()
    years: int | None = None
    periods: tuple[str, ...] = ()
    education: tuple[tuple[str, str | None], ...] = ()
    skills: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    verdicts: tuple[ProfileVerdict, ...] = ()


def _quote(value: str) -> str:
    """Quote a DSL string while preserving backslashes and quotes."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _string_list(values: tuple[str, ...]) -> str:
    return ", ".join(_quote(value) for value in values)


def to_dsl(data: CandidateData) -> str:
    """Serialize candidate data to the textual candidate-profile language."""
    lines = [f"candidate {_quote(data.name or 'Unknown')} {{"]
    if data.emails or data.phones or data.urls:
        lines.append("  contact {")
        if data.emails:
            lines.append(f"    emails: {_string_list(data.emails)}")
        if data.phones:
            lines.append(f"    phones: {_string_list(data.phones)}")
        if data.urls:
            lines.append(f"    urls: {_string_list(data.urls)}")
        lines.append("  }")
    if data.years is not None or data.periods:
        lines.append("  experience {")
        if data.years is not None:
            lines.append(f"    years: {data.years}")
        if data.periods:
            lines.append(f"    periods: {_string_list(data.periods)}")
        lines.append("  }")
    if data.education:
        lines.append("  education {")
        for degree, institution in data.education:
            entry = f"    {_quote(degree)}"
            if institution:
                entry += f" at {_quote(institution)}"
            lines.append(entry)
        lines.append("  }")

    lines.append("  skills {")
    for category, qualifications in data.skills.items():
        if qualifications:
            lines.append(f"    {category}: {', '.join(qualifications)}")
    lines.append("  }")
    lines.append("  classification {")
    for verdict in data.verdicts:
        label = "ACCEPTED" if verdict.accepted else "REJECTED"
        entry = f"    profile {verdict.profile_key}: {label}"
        if verdict.sequence:
            entry += f" sequence [{', '.join(verdict.sequence)}]"
        if verdict.missing:
            entry += f" missing [{_string_list(verdict.missing)}]"
        lines.append(entry)
    lines.extend(("  }", "}"))
    return "\n".join(lines) + "\n"
