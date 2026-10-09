from resumelens.normalization.aliases import ALIASES, canonical_of
from resumelens.profiles import PROFILES


def test_four_profiles_are_defined():
    assert set(PROFILES) == {"full_stack", "ml_engineer", "devops_engineer", "data_engineer"}


def test_every_profile_skill_has_aliases():
    for profile in PROFILES.values():
        for skill in profile.all_skills():
            assert skill in ALIASES, f"{skill} ({profile.name}) has no alias entry"


def test_canonical_order_follows_categories():
    fs = PROFILES["full_stack"]
    assert fs.category_index("JAVASCRIPT") < fs.category_index("REACT") \
        < fs.category_index("NODE_JS") < fs.category_index("POSTGRESQL") \
        < fs.category_index("GIT")
    assert fs.category_index("PYTHON") is None


def test_no_empty_categories():
    for profile in PROFILES.values():
        assert all(c.skills for c in profile.categories)
