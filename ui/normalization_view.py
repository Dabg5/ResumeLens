"""Normalization view for the Streamlit user interface.

Presents the two-level normalization results:
1. Raw extracted surface forms mapped to canonical qualification names.
2. Canonical sorting for each profile according to category sequences,
   explicitly highlighting ignored qualifications.
3. The formal 7-tuple definitions and transition diagrams of the transducers.
"""
import streamlit as st

from resumelens.normalization import Normalization, SortedQualifications, transducers
from resumelens.profiles import PROFILES
from resumelens.viz.diagrams import digraph


def render(
    normalized: list[Normalization],
    sorted_by_profile: dict[str, SortedQualifications],
) -> None:
    """Render the normalization view in Streamlit."""
    st.header("Qualification Normalization (Transducers)")
    st.write(
        "Normalization converts diverse surface spellings into unique canonical "
        "identifiers using formal finite-state transducers, and orders them "
        "according to target profile categories."
    )

    if not normalized:
        st.info("No qualification skills provided for normalization.")
        return

    # --- Section 1: Raw to Canonical Normalization Table ---
    st.subheader("1. Surface Form Normalization")

    recognized_count = sum(1 for n in normalized if n.canonical is not None)
    unmapped_count = len(normalized) - recognized_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Extracted", len(normalized))
    col2.metric("Canonical Recognized", recognized_count)
    col3.metric("Unmapped", unmapped_count)

    table_data = [
        {
            "Raw Extracted": n.raw,
            "Canonical Qualification": n.canonical if n.canonical else "(Unknown / None)",
            "Status": "Recognized" if n.canonical else "Unmapped",
        }
        for n in normalized
    ]
    st.dataframe(table_data, use_container_width=True)

    # --- Section 2: Profile-driven Canonical Sorting ---
    st.subheader("2. Profile-Driven Canonical Sorting")
    st.write(
        "Qualifications are ordered by `(category_index, original_position)`. "
        "Technologies outside the profile are routed to `ignored` and displayed "
        "transparently."
    )

    profile_keys = list(sorted_by_profile.keys())
    tabs = st.tabs([PROFILES[k].name if k in PROFILES else k for k in profile_keys])

    for tab, p_key in zip(tabs, profile_keys):
        with tab:
            sq = sorted_by_profile[p_key]
            prof = PROFILES.get(p_key)

            if sq.sequence:
                st.markdown("**Canonical Sequence for Profile:**")
                st.code(" -> ".join(sq.sequence))
            else:
                st.warning("No qualifications in this résumé match the profile categories.")

            if sq.ignored:
                st.markdown("**Ignored Qualifications (not required by this profile):**")
                st.write(", ".join(f"`{s}`" for s in sq.ignored))
            else:
                st.info("No qualifications were ignored for this profile.")

            if prof:
                with st.expander("View Category Order for Profile"):
                    for idx, cat in enumerate(prof.categories):
                        opt = " (Optional)" if cat.optional else ""
                        st.markdown(f"- **Category {idx}: {cat.name}**{opt}: {', '.join(cat.skills)}")

    # --- Section 3: Formal 7-Tuple & Transition Diagrams ---
    st.subheader("3. Formal Transducer Models & Diagrams")
    st.write(
        "Each transducer is formally defined as a 7-tuple "
        "$T = (Q, \\Sigma, \\Gamma, \\delta, \\omega, q_0, F)$."
    )

    all_transducers = transducers()
    transducer_names = list(all_transducers.keys())
    selected_name = st.selectbox(
        "Select Transducer to Inspect",
        transducer_names,
        format_func=lambda x: f"{x.capitalize()} Transducer ({all_transducers[x].fst_tuple.name})",
    )

    selected_fst = all_transducers[selected_name]
    t = selected_fst.fst_tuple

    with st.expander("Formal 7-Tuple Specification", expanded=True):
        st.markdown(t.as_markdown())

    with st.expander("Transition Diagram", expanded=True):
        if selected_name == "clean":
            dot = digraph(t.name, t.states, t.start_state, t.final_states, t.edges(), merge_parallel=True)
            st.graphviz_chart(dot)
        else:
            st.info(
                f"Trie transducer for `{selected_name}` contains {len(t.states)} states "
                f"and {len(t.transitions)} transitions."
            )
            dot = digraph(t.name, t.states, t.start_state, t.final_states, t.edges(), merge_parallel=False)
            st.graphviz_chart(dot)
