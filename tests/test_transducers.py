import pytest
from pyformlang.fst import FST

from resumelens.normalization import (
    ALIASES,
    alias_key,
    canonical_of,
    clean,
    canonical_skills,
    normalize_all,
    transducers,
    translate,
    build_clean_fst,
    build_lexicon_fst,
    Normalization,
)


def test_pyformlang_fst_smoke():
    f = FST()
    f.add_transition("q0", "a", "q1", ["X"])
    f.add_start_state("q0")
    f.add_final_state("q1")
    assert list(f.translate(["a"])) == [["X"]]
    assert list(f.translate(["b"])) == []


def test_clean_fst_equivalent_to_alias_key():
    for canonical, forms in ALIASES.items():
        for form in (canonical, *forms):
            assert clean(form) == alias_key(form)


def test_clean_fst_separators_and_case():
    cases = {
        "Node.js": "nodejs",
        "React.js": "reactjs",
        "C++": "c++",
        "C#": "c#",
        "Spring-Boot": "springboot",
        "CI/CD": "cicd",
        "Amazon Web Services": "amazonwebservices",
        "Postgre SQL": "postgresql",
    }
    for raw, expected in cases.items():
        assert clean(raw) == expected


def test_clean_fst_empty():
    assert clean("") == ""


def test_clean_fst_invalid_char():
    assert clean("@invalid!") is None


def test_every_alias_form_translates_to_canonical():
    for canonical, forms in ALIASES.items():
        for form in (canonical, *forms):
            assert translate(form) == canonical_of(form) == canonical


def test_end_marker_resolves_prefixes():
    # java vs javascript
    assert translate("Java") == "JAVA"
    assert translate("JavaScript") == "JAVASCRIPT"
    # git vs github
    assert translate("Git") == "GIT"
    assert translate("GitHub") == "GITHUB"

    # Direct check on T_lex: without '$', prefix is not accepted
    all_fsts = transducers()
    lang_fst = all_fsts["languages"]
    assert list(lang_fst.translate(list("java"))) == []
    assert list(lang_fst.translate(list("java$"))) == [["JAVA"]]


def test_unknown_and_json_are_none():
    assert translate("JSON") is None
    assert translate("COBOL-ish thing") is None
    assert translate("unknown_tool") is None
    assert translate("") is None


def test_fst_tuples_are_consistent():
    all_fsts = transducers()
    assert len(all_fsts) == 6

    for name, fst in all_fsts.items():
        t = fst.fst_tuple
        assert t.is_consistent(), f"FST tuple for {name} is inconsistent"
        assert t.start_state in t.states
        assert all(f in t.states for f in t.final_states)
        for src, in_sym, dst, out_syms in t.transitions:
            assert src in t.states
            assert dst in t.states
            assert in_sym in t.input_alphabet
            assert all(o in t.output_alphabet for o in out_syms)


def test_fst_tuple_edges_format():
    all_fsts = transducers()
    clean_edges = all_fsts["clean"].fst_tuple.edges()
    assert any(label == "a : a" for _, label, _ in clean_edges)
    assert any(label == ". : ε" for _, label, _ in clean_edges)

    tools_edges = all_fsts["tools"].fst_tuple.edges()
    assert any(label == "$ : GIT" for _, label, _ in tools_edges)


def test_fst_tuple_as_markdown():
    clean_tuple = transducers()["clean"].fst_tuple
    md = clean_tuple.as_markdown()
    assert "### Transducer: `T_clean`" in md
    assert "Formal 7-tuple definition" in md
    assert "| Source ($q$) | Input ($\\sigma$) | Destination ($q'$) | Output ($\\gamma$) |" in md


def test_normalize_all():
    raw_list = ["React.js", "Python", "JSON", "Docker"]
    normalized = normalize_all(raw_list)
    assert normalized == [
        Normalization("React.js", "REACT"),
        Normalization("Python", "PYTHON"),
        Normalization("JSON", None),
        Normalization("Docker", "DOCKER"),
    ]


def test_canonical_skills_dedupes_and_filters_none():
    raw_list = ["React.js", "Python", "JSON", "React", "Docker", "Python 3"]
    skills = canonical_skills(raw_list)
    assert skills == ("REACT", "PYTHON", "DOCKER")


def test_canonical_skills_empty():
    assert canonical_skills([]) == ()


def test_custom_lexicon_build():
    custom = build_lexicon_fst("custom", {"TOOL_A": ("Tool-A",), "TOOL_B": ("Tool-B",)})
    assert custom.fst_tuple.is_consistent()
    assert list(custom.translate(list("toola$"))) == [["TOOL_A"]]
    assert list(custom.translate(list("toolb$"))) == [["TOOL_B"]]
    assert list(custom.translate(list("toola"))) == []


def test_transducers_dict_keys():
    expected_keys = {"clean", "languages", "frameworks", "databases", "tools", "other"}
    assert set(transducers().keys()) == expected_keys
