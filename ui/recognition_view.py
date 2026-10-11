"""Streamlit view for profile recognition results and automaton models."""
import streamlit as st

from resumelens.profiles import PROFILES
from resumelens.recognition.automata import automata
from resumelens.recognition.classifier import ProfileMatch
from resumelens.viz.diagrams import digraph


def render(matches: tuple[ProfileMatch, ...]) -> None:
    """Render verdicts, traces and the formal automaton for each profile."""
    st.header("Profile Recognition")
    st.caption("Each profile is checked independently; results are not ranked.")
    models = automata()
    tabs = st.tabs([PROFILES[match.profile_key].name for match in matches])
    for tab, match in zip(tabs, matches):
        with tab:
            (st.success if match.accepted else st.error)(
                "ACCEPTED" if match.accepted else "REJECTED"
            )
            st.write("Canonical sequence")
            st.code(" → ".join(match.sequence) if match.sequence else "(empty)")
            if match.missing_categories:
                st.write("Missing required categories: " + ", ".join(match.missing_categories))
            st.write("Recognition trace")
            st.code(" → ".join(match.trace))
            _, formal = models[match.profile_key]
            with st.expander("Formal five-tuple", expanded=True):
                st.markdown(formal.as_markdown())
                st.markdown(f"**Pattern:** `{formal.regex()}`")
            dot = digraph(formal.name, formal.states, formal.start_state,
                          formal.final_states, formal.edges())
            st.graphviz_chart(dot)
