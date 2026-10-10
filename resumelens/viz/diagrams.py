"""Shared transition-diagram builder for transducers and automata.

Both formal models are reduced to the same data: states, a start state,
final states and labelled edges. `st.graphviz_chart` can render the result
without the graphviz binary; `export` needs it.
"""
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

import graphviz

Edge = tuple[str, str, str]  # (source, label, target)


def digraph(
    name: str,
    states: Iterable[str],
    start: str,
    finals: Iterable[str],
    edges: Iterable[Edge],
    *,
    rankdir: str = "LR",
    merge_parallel: bool = True,
) -> graphviz.Digraph:
    """Build a diagram with an arrow into `start` and double circles on `finals`.

    With `merge_parallel`, edges sharing source and target are drawn once with
    their labels joined ("PANDAS, NUMPY"), as in the task statement figures.
    """
    finals = set(finals)
    dot = graphviz.Digraph(name, graph_attr={"rankdir": rankdir})
    dot.attr("node", shape="circle")

    dot.node("__start__", label="", shape="none", width="0", height="0")
    for state in states:
        dot.node(state, shape="doublecircle" if state in finals else "circle")
    dot.edge("__start__", start)

    if merge_parallel:
        grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
        for src, label, dst in edges:
            if label not in grouped[(src, dst)]:
                grouped[(src, dst)].append(label)
        for (src, dst), labels in grouped.items():
            dot.edge(src, dst, label=", ".join(labels))
    else:
        for src, label, dst in edges:
            dot.edge(src, dst, label=label)
    return dot


def export(dot: graphviz.Digraph, stem: str | Path, fmt: str = "svg") -> Path:
    """Write the diagram next to `stem` (requires the graphviz `dot` binary)."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    rendered = dot.render(filename=stem.name, directory=str(stem.parent),
                          format=fmt, cleanup=True)
    return Path(rendered)
