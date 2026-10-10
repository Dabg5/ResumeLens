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


def test_version_control_hosts_count_as_git():
    for profile in PROFILES.values():
        vc = next(c for c in profile.categories if c.name == "Version control")
        assert {"GIT", "GITHUB", "GITLAB", "BITBUCKET"} <= set(vc.skills)


def test_declared_automaton_types():
    assert PROFILES["ml_engineer"].automaton_type == "DFA"
    assert PROFILES["data_engineer"].automaton_type == "DFA"
    assert PROFILES["full_stack"].automaton_type == "ε-NFA"
    assert PROFILES["devops_engineer"].automaton_type == "ε-NFA"


def test_categories_of_a_profile_do_not_share_skills():
    for profile in PROFILES.values():
        skills = profile.all_skills()
        assert len(skills) == len(set(skills)), profile.name


def test_epsilon_nfa_profiles_have_an_optional_category():
    for profile in PROFILES.values():
        has_optional = any(c.optional for c in profile.categories)
        assert has_optional == (profile.automaton_type == "ε-NFA"), profile.name
