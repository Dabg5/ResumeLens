import pytest

from resumelens.normalization.aliases import canonical_of


@pytest.mark.parametrize("text,expected", [
    ("JS", "JAVASCRIPT"), ("Javascript", "JAVASCRIPT"),
    ("React.js", "REACT"), ("ReactJS", "REACT"),
    ("NodeJS", "NODE_JS"), ("Node.js", "NODE_JS"),
    ("Postgres", "POSTGRESQL"), ("PostgreSQL", "POSTGRESQL"),
    ("sklearn", "SCIKIT_LEARN"), ("scikit learn", "SCIKIT_LEARN"), ("Scikit-learn", "SCIKIT_LEARN"),
    ("Tensor Flow", "TENSORFLOW"), ("TensorFlow", "TENSORFLOW"),
    ("Py Torch", "PYTORCH"), ("pandas", "PANDAS"),
    ("k8s", "KUBERNETES"), ("Amazon Web Services", "AWS"),
])
def test_equivalent_spellings(text, expected):
    assert canonical_of(text) == expected


def test_unknown_is_none():
    assert canonical_of("COBOL-ish thing") is None
