"""Streamlit view of extracted résumé fields."""
import streamlit as st

from resumelens.extraction.extractor import ExtractionResult


def render(result: ExtractionResult) -> None:
    """Show contact, experience, education and raw qualification extraction."""
    st.header("Résumé Extraction")
    st.write(f"**Name:** {result.name or 'Unknown'}")
    left, right = st.columns(2)
    with left:
        st.subheader("Contact")
        st.write({"Emails": result.emails, "Phones": result.phones, "URLs": result.urls})
        st.subheader("Experience")
        st.write({"Years": result.years_of_experience, "Periods": result.date_ranges})
    with right:
        st.subheader("Education")
        st.write({"Degrees": result.degrees, "Institutions": result.institutions})
        st.subheader("Extracted qualifications")
        st.write(result.skills)
