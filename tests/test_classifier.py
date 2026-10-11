import pytest

from resumelens.profiles import PROFILES
from resumelens.recognition.classifier import accepted_profiles, classify, classify_all


def test_classify_accepts_full_stack_and_reports_trace():
    match = classify("full_stack", ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"))
    assert match.accepted
    assert match.profile_name == "Full Stack Developer"
    assert match.missing_categories == ()
    assert match.trace[0] == "q0" and "GIT" in match.trace[-1]


def test_classify_rejects_and_reports_missing_category():
    match = classify("full_stack", ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"))
    assert not match.accepted
    assert match.missing_categories == ("Version control",)


def test_classify_all_preserves_profile_order_without_ranking():
    sequences = {
        "full_stack": ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"),
        "ml_engineer": ("PYTHON", "PANDAS", "SCIKIT_LEARN", "SQL", "GIT"),
    }
    matches = classify_all(sequences)
    assert tuple(m.profile_key for m in matches) == tuple(PROFILES)
    assert matches[0].accepted and matches[1].accepted
    assert not any(hasattr(match, "score") for match in matches)


def test_accepted_profiles_returns_all_matches():
    matches = classify_all({
        "full_stack": ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"),
        "ml_engineer": ("PYTHON", "PANDAS", "SCIKIT_LEARN", "SQL", "GIT"),
    })
    accepted = accepted_profiles(matches)
    assert tuple(m.profile_key for m in accepted) == ("full_stack", "ml_engineer")


def test_unknown_profile_raises_key_error():
    with pytest.raises(KeyError, match="unknown profile"):
        classify("unknown", ())
