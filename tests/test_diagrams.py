import shutil

import pytest

from resumelens.viz.diagrams import digraph, export

EDGES = [("q0", "PYTHON", "q1"), ("q1", "PANDAS", "q2"), ("q1", "NUMPY", "q2")]


def make(**kwargs):
    return digraph("M", ["q0", "q1", "q2"], "q0", ["q2"], EDGES, **kwargs)


def test_final_states_are_double_circles():
    source = make().source
    assert "q2 [shape=doublecircle]" in source
    assert "q0 [shape=circle]" in source


def test_start_arrow_points_to_start_state():
    assert "__start__ -> q0" in make().source


def test_parallel_edges_are_merged():
    source = make().source
    assert "q1 -> q2 [label=\"PANDAS, NUMPY\"]" in source
    assert source.count("q1 -> q2") == 1


def test_parallel_edges_can_stay_separate():
    source = make(merge_parallel=False).source
    assert source.count("q1 -> q2") == 2


def test_duplicate_labels_are_not_repeated():
    dot = digraph("M", ["a", "b"], "a", ["b"], [("a", "X", "b"), ("a", "X", "b")])
    assert dot.source.count("X") == 1


@pytest.mark.skipif(shutil.which("dot") is None, reason="graphviz binary not installed")
def test_export_svg(tmp_path):
    path = export(make(), tmp_path / "m", "svg")
    assert path.suffix == ".svg" and path.exists()
