"""Finite-state transducers for qualification normalization.

Normalization maps diverse surface forms (e.g. 'Node.js', 'ReactJS', 'JS')
to canonical qualification names (e.g. 'NODE_JS', 'REACT', 'JAVASCRIPT').

The formal process consists of two sequential transducer levels:
1. T_clean (single state): maps characters to lower case and eliminates
   punctuation separators (. - _ / and whitespace), outputting epsilon.
2. T_lex[g] (one per category group): a character-level trie constructed
   from alias keys with an end marker '$' that emits the canonical name.
   The end marker unambiguously resolves prefix overlaps (e.g. 'java' vs
   'javascript', 'git' vs 'github').
"""
from dataclasses import dataclass
from collections.abc import Iterable
from functools import lru_cache

from pyformlang.fst import FST

from .aliases import ALIASES, alias_key


@dataclass(frozen=True)
class Normalization:
    """Mapping from a raw extracted skill string to its canonical form."""
    raw: str
    canonical: str | None


@dataclass(frozen=True)
class FstTuple:
    """Formal 7-tuple representation of a Finite-State Transducer (FST).

    T = (Q, Σ, Γ, δ, ω, q0, F)
    - Q: finite set of states
    - Σ: input alphabet
    - Γ: output alphabet
    - transitions: (source, input_symbol, destination, output_symbols)
    - q0: initial state
    - F: set of final states
    """
    name: str
    states: tuple[str, ...]
    input_alphabet: tuple[str, ...]
    output_alphabet: tuple[str, ...]
    transitions: tuple[tuple[str, str, str, tuple[str, ...]], ...]
    start_state: str
    final_states: tuple[str, ...]

    def edges(self) -> list[tuple[str, str, str]]:
        """Return (source, label, destination) transitions for diagram visualization.

        Labels use the format 'input : output' (or 'input : ε' for empty output).
        """
        result: list[tuple[str, str, str]] = []
        for src, in_sym, dst, out_syms in self.transitions:
            out_label = ",".join(out_syms) if out_syms else "ε"
            result.append((src, f"{in_sym} : {out_label}", dst))
        return result

    def as_markdown(self) -> str:
        """Markdown representation of the 7-tuple definition and transition table."""
        sample_states = ", ".join(sorted(self.states)[:15])
        if len(self.states) > 15:
            sample_states += f", ... ({len(self.states)} total)"

        lines = [
            f"### Transducer: `{self.name}`",
            "",
            "**Formal 7-tuple definition** $T = (Q, \\Sigma, \\Gamma, \\delta, \\omega, q_0, F)$:",
            f"- **$Q$** ({len(self.states)} states): `{sample_states}`",
            f"- **$\\Sigma$** ({len(self.input_alphabet)} input symbols): `{', '.join(sorted(self.input_alphabet))}`",
            f"- **$\\Gamma$** ({len(self.output_alphabet)} output symbols): `{', '.join(sorted(self.output_alphabet))}`",
            f"- **$q_0$** (start state): `{self.start_state}`",
            f"- **$F$** (final states): `{', '.join(sorted(self.final_states))}`",
            "",
            "| Source ($q$) | Input ($\\sigma$) | Destination ($q'$) | Output ($\\gamma$) |",
            "|---|---|---|---|",
        ]
        for src, in_sym, dst, out_syms in self.transitions:
            out_str = ", ".join(out_syms) if out_syms else "ε"
            lines.append(f"| `{src}` | `{in_sym}` | `{dst}` | `{out_str}` |")
        return "\n".join(lines)

    def is_consistent(self) -> bool:
        """Verify that start and final states belong to Q, and all transitions respect Q, Σ, Γ."""
        q_set = set(self.states)
        sigma_set = set(self.input_alphabet)
        gamma_set = set(self.output_alphabet)

        if self.start_state not in q_set:
            return False
        if not all(f in q_set for f in self.final_states):
            return False
        for src, in_sym, dst, out_syms in self.transitions:
            if src not in q_set or dst not in q_set:
                return False
            if in_sym not in sigma_set:
                return False
            if not all(o in gamma_set for o in out_syms):
                return False
        return True


GROUPED_CANONICALS: dict[str, tuple[str, ...]] = {
    "languages": (
        "JAVASCRIPT", "TYPESCRIPT", "PYTHON", "JAVA", "CSHARP", "CPP",
        "PHP", "RUBY", "KOTLIN", "SWIFT", "BASH",
    ),
    "frameworks": (
        "REACT", "ANGULAR", "VUE", "NODE_JS", "EXPRESS", "NEXT_JS",
        "DJANGO", "FLASK", "FASTAPI", "SPRING_BOOT", "PANDAS", "NUMPY",
        "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS", "PYSPARK",
    ),
    "databases": (
        "SQL", "POSTGRESQL", "MYSQL", "MARIADB", "SQLITE", "SQL_SERVER",
        "ORACLE", "MONGODB", "REDIS", "CASSANDRA", "DYNAMODB", "FIREBASE",
        "BIGQUERY", "SNOWFLAKE", "REDSHIFT",
    ),
    "tools": (
        "GIT", "GITHUB", "GITLAB", "BITBUCKET", "DOCKER", "KUBERNETES",
        "JENKINS", "GITHUB_ACTIONS", "GITLAB_CI", "TERRAFORM", "ANSIBLE",
        "LINUX", "AWS", "AZURE", "GCP", "AIRFLOW", "KAFKA", "JIRA", "POSTMAN",
    ),
    "other": (
        "REST_API", "GRAPHQL", "MACHINE_LEARNING", "DEEP_LEARNING",
        "CI_CD", "AGILE", "SCRUM", "MICROSERVICES",
    ),
}

# Separators mapped to epsilon in T_clean
_SEPARATORS = (".", "-", "_", "/", " ", "\t")
_LETTERS_LOWER = tuple("abcdefghijklmnopqrstuvwxyz")
_LETTERS_UPPER = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_DIGITS = tuple("0123456789")
_SPECIAL = ("+", "#")


def build_clean_fst() -> FST:
    """Build the single-state cleaning transducer T_clean.

    Converts characters to lower case and deletes punctuation separators
    (. - _ / and whitespace), outputting epsilon.
    """
    fst = FST()
    start_state = "q0"
    fst.add_start_state(start_state)
    fst.add_final_state(start_state)

    raw_transitions: list[tuple[str, str, str, tuple[str, ...]]] = []

    # Lowercase characters -> identity output
    for c in (*_LETTERS_LOWER, *_DIGITS, *_SPECIAL):
        fst.add_transition(start_state, c, start_state, [c])
        raw_transitions.append((start_state, c, start_state, (c,)))

    # Uppercase characters -> lowercase output
    for c in _LETTERS_UPPER:
        out_c = c.lower()
        fst.add_transition(start_state, c, start_state, [out_c])
        raw_transitions.append((start_state, c, start_state, (out_c,)))

    # Separators -> epsilon output (empty list)
    for sep in _SEPARATORS:
        fst.add_transition(start_state, sep, start_state, [])
        raw_transitions.append((start_state, sep, start_state, ()))

    input_alphabet = tuple(sorted({t[1] for t in raw_transitions}))
    output_alphabet = tuple(sorted({o for t in raw_transitions for o in t[3]}))

    fst.fst_tuple = FstTuple(
        name="T_clean",
        states=(start_state,),
        input_alphabet=input_alphabet,
        output_alphabet=output_alphabet,
        transitions=tuple(raw_transitions),
        start_state=start_state,
        final_states=(start_state,),
    )
    return fst


def build_lexicon_fst(name: str, aliases: dict[str, tuple[str, ...]]) -> FST:
    """Build a lexicon trie transducer T_lex for a qualification group.

    Consumes alias keys character-by-character emitting epsilon, and on the
    end marker '$' transitions to the final state emitting the canonical name.
    """
    fst = FST()
    start_state = "q0"
    final_state = "q_final"
    fst.add_start_state(start_state)
    fst.add_final_state(final_state)

    # Collect unique (alias_key, canonical) pairs
    entries: dict[str, str] = {}
    for canonical, forms in aliases.items():
        for form in (canonical, *forms):
            key = alias_key(form)
            entries[key] = canonical

    trie_nodes: dict[str, str] = {"": start_state}
    state_counter = 0
    raw_transitions: list[tuple[str, str, str, tuple[str, ...]]] = []

    for key, canonical in sorted(entries.items()):
        curr_state = start_state
        curr_prefix = ""
        for ch in key:
            next_prefix = curr_prefix + ch
            if next_prefix not in trie_nodes:
                state_counter += 1
                next_state = f"q{state_counter}"
                trie_nodes[next_prefix] = next_state
                fst.add_transition(curr_state, ch, next_state, [])
                raw_transitions.append((curr_state, ch, next_state, ()))
            curr_state = trie_nodes[next_prefix]
            curr_prefix = next_prefix

        # End marker transition emits canonical qualification
        fst.add_transition(curr_state, "$", final_state, [canonical])
        raw_transitions.append((curr_state, "$", final_state, (canonical,)))

    states = tuple(sorted(set(trie_nodes.values()) | {final_state}))
    input_alphabet = tuple(sorted({t[1] for t in raw_transitions}))
    output_alphabet = tuple(sorted({o for t in raw_transitions for o in t[3]}))

    fst.fst_tuple = FstTuple(
        name=f"T_lex_{name}",
        states=states,
        input_alphabet=input_alphabet,
        output_alphabet=output_alphabet,
        transitions=tuple(raw_transitions),
        start_state=start_state,
        final_states=(final_state,),
    )
    return fst


@lru_cache(maxsize=1)
def _cached_clean_fst() -> FST:
    return build_clean_fst()


@lru_cache(maxsize=1)
def _cached_lexicon_fsts() -> dict[str, FST]:
    fsts: dict[str, FST] = {}
    for group_name, canonicals in GROUPED_CANONICALS.items():
        group_aliases = {c: ALIASES[c] for c in canonicals if c in ALIASES}
        fsts[group_name] = build_lexicon_fst(group_name, group_aliases)
    return fsts


def transducers() -> dict[str, FST]:
    """Return all normalization transducers: clean and group lexicons."""
    return {
        "clean": _cached_clean_fst(),
        **_cached_lexicon_fsts(),
    }


def clean(text: str) -> str | None:
    """Normalize raw text with T_clean: lower-cased without separators."""
    if not text:
        return ""
    fst = _cached_clean_fst()
    results = list(fst.translate(list(text)))
    if not results:
        return None
    return "".join(results[0])


def translate(text: str) -> str | None:
    """Translate a surface qualification to its canonical name using two-level transducers.

    Returns the canonical name or None if not recognized.
    """
    cleaned = clean(text)
    if cleaned is None or not cleaned:
        return None

    word = list(cleaned + "$")
    for fst in _cached_lexicon_fsts().values():
        res = list(fst.translate(word))
        if res and res[0]:
            return res[0][0]
    return None


def normalize_all(raw: Iterable[str]) -> list[Normalization]:
    """Normalize an iterable of raw extracted strings."""
    return [Normalization(item, translate(item)) for item in raw]


def canonical_skills(raw: Iterable[str]) -> tuple[str, ...]:
    """Return recognized canonical skills in order of appearance, without None or duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for item in raw:
        canonical = translate(item)
        if canonical is not None and canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return tuple(result)
