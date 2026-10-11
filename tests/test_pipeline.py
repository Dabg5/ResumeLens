from pathlib import Path

from resumelens.pipeline import run


ROOT = Path(__file__).resolve().parents[1]


def test_pipeline_produces_valid_dsl_and_all_profile_results():
    sample = (ROOT / "samples" / "wednesday_addams.txt").read_text(encoding="utf-8")
    result = run(sample)
    assert result.validation.valid, result.validation.errors
    assert result.extraction.name == "Wednesday Addams"
    assert len(result.normalized) == len(result.extraction.skills)
    assert set(result.sorted_by_profile) == {
        "full_stack", "ml_engineer", "devops_engineer", "data_engineer"
    }
    assert "Candidate: Wednesday Addams" in result.markdown
    assert "candidate-card" in result.html


def test_pipeline_classifies_reference_full_stack_resume():
    sample = (ROOT / "samples" / "wednesday_addams.txt").read_text(encoding="utf-8")
    result = run(sample)
    accepted = [match.profile_key for match in result.matches if match.accepted]
    assert accepted == ["full_stack"]


def test_end_to_end_reference_samples_match_expected_profiles():
    expectations = {
        "wednesday_addams.txt": {"full_stack"},
        "mary_jane_watson.txt": {"ml_engineer"},
        "devops_engineer.txt": {"devops_engineer"},
        "data_engineer.txt": {"data_engineer"},
        "full_stack_complete.txt": {"full_stack"},
        "rejected_missing_version_control.txt": set(),
        "noisy_spelling_variants.txt": set(),
    }
    for filename, expected in expectations.items():
        result = run((ROOT / "samples" / filename).read_text(encoding="utf-8"))
        assert result.validation.valid, (filename, result.validation.errors)
        actual = {match.profile_key for match in result.matches if match.accepted}
        assert actual == expected, filename


def test_missing_version_control_is_explained_in_end_to_end_result():
    result = run((ROOT / "samples" / "rejected_missing_version_control.txt")
                 .read_text(encoding="utf-8"))
    full_stack = next(match for match in result.matches if match.profile_key == "full_stack")
    assert not full_stack.accepted
    assert full_stack.missing_categories == ("Version control",)


def test_noisy_variants_normalize_without_duplicates_and_do_not_match():
    result = run((ROOT / "samples" / "noisy_spelling_variants.txt")
                 .read_text(encoding="utf-8"))
    canonicals = [item.canonical for item in result.normalized if item.canonical]
    assert len(canonicals) > len(set(canonicals))
    assert not any(match.accepted for match in result.matches)
