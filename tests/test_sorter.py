import pytest

from resumelens.normalization.sorter import SortedQualifications, sort_for_all, sort_for_profile
from resumelens.profiles import DATA_ENGINEER, DEVOPS_ENGINEER, FULL_STACK, ML_ENGINEER, PROFILES


def test_task_statement_full_stack_order():
    """Reproduces the exact sorting example given in the task statement."""
    canonicals = ["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"]
    sorted_q = sort_for_profile(canonicals, FULL_STACK)
    assert sorted_q.sequence == ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT")
    assert sorted_q.ignored == ()
    assert sorted_q.profile_key == "full_stack"


def test_ignored_skills_routed_separately():
    """Skills not part of the profile are kept in `ignored` in appearance order."""
    canonicals = ["PYTHON", "DOCKER", "JAVASCRIPT", "GIT", "AWS"]
    sorted_q = sort_for_profile(canonicals, FULL_STACK)
    assert sorted_q.sequence == ("JAVASCRIPT", "GIT")
    assert sorted_q.ignored == ("PYTHON", "DOCKER", "AWS")


def test_deduplication():
    """Repeated occurrences of a qualification are kept once."""
    canonicals = ["JAVASCRIPT", "REACT", "JAVASCRIPT", "REACT", "GIT"]
    sorted_q = sort_for_profile(canonicals, FULL_STACK)
    assert sorted_q.sequence == ("JAVASCRIPT", "REACT", "GIT")
    assert sorted_q.ignored == ()


def test_multiple_skills_in_same_category_preserves_original_order():
    """Multiple skills within the same category preserve their relative order of appearance."""
    canonicals = ["NUMPY", "PYTHON", "PANDAS", "GIT"]
    sorted_q = sort_for_profile(canonicals, ML_ENGINEER)
    # Python is Category 0; NumPy (pos 0) and Pandas (pos 2) are Category 1; Git is Category 4
    assert sorted_q.sequence == ("PYTHON", "NUMPY", "PANDAS", "GIT")
    assert sorted_q.ignored == ()


def test_empty_canonicals():
    sorted_q = sort_for_profile([], FULL_STACK)
    assert sorted_q.sequence == ()
    assert sorted_q.ignored == ()


def test_all_ignored():
    canonicals = ["AWS", "DOCKER", "KUBERNETES"]
    sorted_q = sort_for_profile(canonicals, FULL_STACK)
    assert sorted_q.sequence == ()
    assert sorted_q.ignored == ("AWS", "DOCKER", "KUBERNETES")


def test_sort_for_all():
    canonicals = ["PYTHON", "SQL", "PANDAS", "GIT", "REACT"]
    all_sorted = sort_for_all(canonicals)
    assert set(all_sorted.keys()) == set(PROFILES.keys())

    ml_res = all_sorted["ml_engineer"]
    assert "REACT" in ml_res.ignored
    assert "PANDAS" in ml_res.sequence

    fs_res = all_sorted["full_stack"]
    assert "PANDAS" in fs_res.ignored
    assert "REACT" in fs_res.sequence


def test_devops_profile_sorting():
    canonicals = ["GIT", "TERRAFORM", "AWS", "JENKINS", "DOCKER", "PYTHON", "KUBERNETES"]
    sorted_q = sort_for_profile(canonicals, DEVOPS_ENGINEER)
    assert sorted_q.sequence == ("PYTHON", "DOCKER", "KUBERNETES", "JENKINS", "AWS", "TERRAFORM", "GIT")
    assert sorted_q.ignored == ()


def test_data_engineer_profile_sorting():
    canonicals = ["GIT", "BIGQUERY", "AIRFLOW", "PANDAS", "SQL", "PYTHON"]
    sorted_q = sort_for_profile(canonicals, DATA_ENGINEER)
    assert sorted_q.sequence == ("PYTHON", "SQL", "PANDAS", "AIRFLOW", "BIGQUERY", "GIT")
    assert sorted_q.ignored == ()
