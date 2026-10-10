"""Streamlit view for candidate DSL editing and rendered previews."""
import streamlit as st
import streamlit.components.v1 as components

from resumelens.dsl.renderer import to_html, to_markdown
from resumelens.dsl.serializer import CandidateData, to_dsl
from resumelens.dsl.validator import validate


def render(data: CandidateData) -> None:
    """Show generated DSL, validate edits, and offer Markdown/HTML downloads."""
    generated = to_dsl(data)
    original_report = validate(generated)

    st.header("Candidate DSL")
    st.caption("The candidate record expressed in the ResumeLens domain language.")
    st.code(generated, language="text")
    edited = st.text_area("Edit the DSL to validate it", value=generated, height=320)
    report = validate(edited)

    if report.valid:
        st.success("The DSL is valid.")
        model = report.model
    else:
        st.error("The edited DSL is invalid.")
        for error in report.errors:
            st.write(f"- {error}")
        model = original_report.model

    if model is None:
        st.error("The generated candidate DSL could not be validated.")
        return

    markdown = to_markdown(model)
    html = to_html(model)
    st.subheader("Rendered candidate card")
    components.html(html, height=520, scrolling=True)
    col_md, col_html = st.columns(2)
    col_md.download_button(
        "Download Markdown", markdown, file_name="candidate.md", mime="text/markdown"
    )
    col_html.download_button(
        "Download HTML", html, file_name="candidate.html", mime="text/html"
    )
