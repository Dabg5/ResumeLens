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
