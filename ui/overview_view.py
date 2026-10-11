"""Compact overview of the full processing result."""
import streamlit as st

from resumelens.pipeline import PipelineResult


def render(result: PipelineResult) -> None:
    """Summarize extraction quality and profile decisions."""
    st.header("Full Pipeline")
    accepted = [match.profile_name for match in result.matches if match.accepted]
    if accepted:
        st.success("Profiles accepted: " + ", ".join(accepted))
    else:
        st.info("No profile matched the complete required qualification pattern.")
    st.metric("Extracted skills", len(result.extraction.skills))
    st.metric("Canonical qualifications", sum(item.canonical is not None for item in result.normalized))
    st.metric("Valid candidate DSL", "Yes" if result.validation.valid else "No")
    if not result.validation.valid:
        st.error("; ".join(result.validation.errors))
    st.subheader("Candidate summary")
    if result.validation.valid:
        st.markdown(result.markdown)
    st.download_button("Download candidate DSL", result.dsl, "candidate.resumelens", "text/plain")
    if result.validation.valid:
        st.download_button("Download candidate HTML", result.html, "candidate.html", "text/html")
