from pathlib import Path

import pytest

from resumelens.extraction.extractor import extract
from resumelens.normalization.aliases import canonical_of

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def sample(name: str):
    return extract((SAMPLES / name).read_text(encoding="utf-8"))


def test_wednesday_addams_matches_statement():
    r = sample("wednesday_addams.txt")
    assert r.name == "Wednesday Addams"
    assert r.skills == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert r.years_of_experience == ["3 years of experience"]


def test_mary_jane_watson():
    r = sample("mary_jane_watson.txt")
    assert r.skills == ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git"]


def test_contact_information():
    r = sample("full_stack_complete.txt")
    assert r.emails == ["peter.parker@example.com"]
    assert r.phones == ["+57 300 123 4567"]
    assert r.urls == ["https://github.com/pparker", "linkedin.com/in/pparker"]


def test_urls_and_emails_are_not_technologies():
    r = sample("full_stack_complete.txt")
    assert r.skills.count("GitHub") == 1
    assert "github" not in r.skills


def test_education_and_experience():
    r = sample("full_stack_complete.txt")
    assert r.degrees == ["Bachelor of Science in Computer Science"]
    assert r.institutions == ["Universidad Icesi"]
    assert r.date_ranges == ["2019 - 2022", "2022 - present"]
    assert r.years_of_experience == ["4+ years of experience"]
    assert "REST APIs" in r.other


def test_word_boundaries():
    r = extract("JSON, GitHub, NoSQL, javascripting")
    assert "JS" not in r.skills
    assert r.skills == ["GitHub"]


def test_nodejs_is_not_also_js():
    assert extract("Node.js").skills == ["Node.js"]


def test_short_digit_runs_are_not_phones():
    assert extract("Worked 2019 - 2022 on 12345 things").phones == []


def test_empty_text():
    r = extract("")
    assert r.name is None and r.skills == []


@pytest.mark.parametrize("name", [p.name for p in sorted(SAMPLES.glob("*.txt"))])
def test_every_extracted_skill_has_a_canonical_form(name):
    for skill in sample(name).skills:
        assert canonical_of(skill) is not None, f"{skill!r} in {name} has no alias"


def test_save_json(tmp_path):
    out = tmp_path / "r.json"
    sample("wednesday_addams.txt").save(out)
    assert "React.js" in out.read_text(encoding="utf-8")


@pytest.mark.parametrize("text,expected", [
    ("Ingeniería de Sistemas", "Ingeniería de Sistemas"),
    ("Ingeniería Informática", "Ingeniería Informática"),
    ("Ingeniería de Sistemas y Computación", "Ingeniería de Sistemas y Computación"),
    ("Bachelor of Science in Computer Science", "Bachelor of Science in Computer Science"),
    ("B.Sc. in Mathematics", "B.Sc. in Mathematics"),
])
def test_degrees(text, expected):
    assert extract(text).degrees == [expected]


def test_ingenieria_alone_is_not_a_degree():
    assert extract("trabajo de ingeniería general").degrees == []
