"""Applies the regular expressions to a résumé text."""
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .patterns import NAME_PATTERN, PATTERNS, SKILL_CATEGORIES

_TRAILING = ".,;:)]"


@dataclass
class ExtractionResult:
    name: str | None = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    years_of_experience: list[str] = field(default_factory=list)
    date_ranges: list[str] = field(default_factory=list)
    degrees: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    databases: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)
    # Every technology string in the order it appears: input of the normalization step.
    skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _clean(text: str) -> str:
    return text.strip().rstrip(_TRAILING)


def _digits(text: str) -> int:
    return sum(c.isdigit() for c in text)


def extract(text: str) -> ExtractionResult:
    """Extract candidate data and qualification strings from `text`.

    Technology matches of all categories are resolved together so that the
    longest, earliest match wins (e.g. 'GitHub Actions' is one tool, not
    'GitHub' plus something else).
    """
    result = ExtractionResult()

    name = NAME_PATTERN.compile().search(text)
    result.name = name.group(1).strip() if name else None

    by_name: dict[str, list[str]] = {}
    skill_matches: list[tuple[int, int, str, str]] = []  # start, end, category, text
    contact_spans: list[tuple[int, int]] = []  # emails/URLs are not technologies
    for spec in PATTERNS:
        for m in spec.compile().finditer(text):
            value = _clean(m.group(0))
            if spec.name == "phone" and not 7 <= _digits(value) <= 15:
                continue
            if spec.category in SKILL_CATEGORIES:
                skill_matches.append((m.start(), m.end(), spec.category, value))
            else:
                by_name.setdefault(spec.name, []).append(value)
                if spec.name in ("email", "url"):
                    contact_spans.append((m.start(), m.end()))

    result.emails = _dedupe(by_name.get("email", []))
    result.phones = _dedupe(by_name.get("phone", []))
    result.urls = _dedupe(by_name.get("url", []))
    result.years_of_experience = _dedupe(by_name.get("years_of_experience", []))
    result.date_ranges = _dedupe(by_name.get("date_range", []))
    result.degrees = _dedupe(by_name.get("degree", []))
    result.institutions = _dedupe(by_name.get("institution", []))

    skill_matches.sort(key=lambda m: (m[0], -(m[1] - m[0])))
    last_end = -1
    in_order: list[str] = []
    for start, end, category, value in skill_matches:
        if start < last_end or any(start < e and s < end for s, e in contact_spans):
            continue
        last_end = end
        getattr(result, category).append(value)
        in_order.append(value)

    for category in SKILL_CATEGORIES:
        setattr(result, category, _dedupe(getattr(result, category)))
    result.skills = _dedupe(in_order)
    return result
