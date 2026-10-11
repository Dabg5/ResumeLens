from resumelens.profiles import PROFILES
from resumelens.recognition.automata import automata, build_automaton, infer_kind, simulate


def test_each_profile_automaton_kind_matches_its_definition():
    for profile_key, profile in PROFILES.items():
        _, tuple_view = build_automaton(profile)
        assert infer_kind(tuple_view) == profile.automaton_type


def test_profile_automata_accept_and_reject_expected_sequences():
    models = automata()
    accepted = {
        "full_stack": ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"),
        "ml_engineer": ("PYTHON", "PANDAS", "SCIKIT_LEARN", "SQL", "GIT"),
        "devops_engineer": ("PYTHON", "DOCKER", "KUBERNETES", "JENKINS", "AWS", "GIT"),
        "data_engineer": ("PYTHON", "SQL", "PANDAS", "AIRFLOW", "BIGQUERY", "GIT"),
    }
    for key, sequence in accepted.items():
        automaton, tuple_view = models[key]
        assert automaton.accepts(sequence)
        assert simulate(tuple_view, sequence)
        assert not automaton.accepts(sequence[:-1])
        assert not simulate(tuple_view, sequence[:-1])


def test_full_stack_accepts_with_and_without_optional_api():
    automaton, tuple_view = automata()["full_stack"]
    without_api = ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT")
    with_api = ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API", "GIT")
    assert automaton.accepts(without_api) and simulate(tuple_view, without_api)
    assert automaton.accepts(with_api) and simulate(tuple_view, with_api)


def test_full_stack_rejects_missing_version_control():
    automaton, tuple_view = automata()["full_stack"]
    sequence = ("JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL")
    assert not automaton.accepts(sequence)
    assert not simulate(tuple_view, sequence)


def test_choices_within_category_are_alternatives():
    automaton, tuple_view = automata()["ml_engineer"]
    for library in ("PANDAS", "NUMPY"):
        sequence = ("PYTHON", library, "SCIKIT_LEARN", "SQL", "GIT")
        assert automaton.accepts(sequence)
        assert simulate(tuple_view, sequence)


def test_tuple_exposes_states_alphabet_and_regex():
    _, t = automata()["full_stack"]
    assert t.states[0] == t.start_state == "q0"
    assert t.final_states == ("q6",)
    assert "(REST_API)*" in t.regex()
    assert "| q0 | JAVASCRIPT | q1 |" in t.as_markdown()


def test_infer_kind_detects_nondeterminism_and_epsilon():
    assert infer_kind((("q0", "A", "q1"), ("q0", "A", "q2"))) == "NFA"
    assert infer_kind((("q0", "ε", "q1"),)) == "ε-NFA"
