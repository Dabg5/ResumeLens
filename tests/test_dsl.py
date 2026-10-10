"""Tests for the candidate DSL grammar, serializer and validator."""
import pytest

from resumelens.dsl.serializer import CandidateData, ProfileVerdict, to_dsl
from resumelens.dsl.renderer import to_html, to_markdown
from resumelens.dsl.validator import validate


@pytest.fixture
def candidate() -> CandidateData:
    return CandidateData(
        name='Ada "Lovelace" \\ Team',
        emails=("ada@example.com",),
        phones=("+57 300 123 4567",),
        urls=("https://example.com/ada",),
        years=4,
        periods=("2021 - 2025",),
        education=(("B.Sc. Computer Science", "Icesi University"),),
        skills={"languages": ("JAVASCRIPT",), "frameworks": ("REACT",)},
        verdicts=(
            ProfileVerdict("full_stack", True, ("JAVASCRIPT", "REACT")),
            ProfileVerdict("ml_engineer", False, missing=("Languages",)),
        ),
    )


def test_serializer_round_trip_is_valid(candidate: CandidateData) -> None:
    source = to_dsl(candidate)
    report = validate(source)
    assert report.valid, report.errors
    assert '\\"' in source
    assert "\\\\" in source


def test_empty_name_becomes_unknown() -> None:
    source = to_dsl(CandidateData(name=""))
    report = validate(source)
    assert report.valid
    assert report.model.name == "Unknown"


def test_markdown_renderer_includes_candidate_and_verdict(candidate: CandidateData) -> None:
    model = validate(to_dsl(candidate)).model
    markdown = to_markdown(model)
    assert "# Candidate: Ada" in markdown
    assert "full_stack: ACCEPTED" in markdown
    assert "ml_engineer: REJECTED" in markdown


def test_html_renderer_escapes_text_and_shows_verdict_badges() -> None:
    source = to_dsl(
        CandidateData(
            name="<script>alert(1)</script>",
            skills={"languages": ("PYTHON",)},
            verdicts=(
                ProfileVerdict("ml_engineer", True, ("PYTHON",)),
                ProfileVerdict("full_stack", False, missing=("Version control",)),
            ),
        )
    )
    model = validate(source).model
    html = to_html(model)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html
    assert 'class="badge accepted"' in html
    assert 'class="badge rejected"' in html


@pytest.mark.parametrize(
    ("source", "fragment"),
    [
        ('candidate "Ada" { skills { languages: PYTHON } classification { }', "line"),
        ('candidate "Ada" { skills { languages: python } classification { } }', "line"),
        ('candidate "Ada" { skills { languages: PYTHON } classification { profile unknown: REJECTED } }', "unknown profile"),
        ('candidate "Ada" { skills { languages: PYTHON } classification { profile full_stack: ACCEPTED } }', "requires a sequence"),
        ('candidate "Ada { skills { languages: PYTHON } classification { } }', "line"),
        ('candidate "Ada" { skills { languages: PYTHON languages: JAVA } classification { } }', "repeated skill category"),
        ('candidate "Ada" { skills { languages: COBOL } classification { } }', "unknown canonical"),
        ('candidate "Ada" { skills { languages: PYTHON } classification { profile full_stack: REJECTED sequence [PYTHON] } }', "outside profile alphabet"),
    ],
)
def test_invalid_sources_are_rejected(source: str, fragment: str) -> None:
    report = validate(source)
    assert not report.valid
    assert any(fragment in error for error in report.errors)
