"""ResumeLens Streamlit application."""
from pathlib import Path

import streamlit as st

from resumelens.pipeline import run
from ui.dsl_view import render as render_dsl
from ui.extraction_view import render as render_extraction
from ui.normalization_view import render as render_normalization
from ui.overview_view import render as render_overview
from ui.recognition_view import render as render_recognition


@st.cache_data(show_spinner="Processing résumé…")
def cached_run(text: str):
    """Cache the deterministic pipeline result for the current résumé text."""
    return run(text)


st.set_page_config(page_title="ResumeLens", layout="wide")
st.title("ResumeLens")
st.caption("Formal language-based résumé screening")

sample_paths = sorted(Path("samples").glob("*.txt"))
sample_names = [path.name for path in sample_paths]
selected = st.sidebar.selectbox("Example résumé", ["Paste or upload", *sample_names])
uploaded = st.sidebar.file_uploader("Upload a .txt résumé", type=("txt",))

if uploaded is not None:
    text = uploaded.getvalue().decode("utf-8", errors="replace")
elif selected != "Paste or upload":
    sample_text = Path("samples", selected).read_text(encoding="utf-8")
    text = st.text_area("Résumé text", value=sample_text, height=280)
else:
    text = st.text_area("Paste résumé text", height=280,
                        placeholder="Paste plain-text résumé content…")

if text.strip():
    result = cached_run(text)
    extraction_tab, normalization_tab, recognition_tab, dsl_tab, overview_tab = st.tabs(
        ["Extraction", "Normalization", "Recognition", "DSL", "Full pipeline"]
    )
    with extraction_tab:
        render_extraction(result.extraction)
    with normalization_tab:
        render_normalization(list(result.normalized), result.sorted_by_profile)
    with recognition_tab:
        render_recognition(result.matches)
    with dsl_tab:
        render_dsl(result.candidate)
    with overview_tab:
        render_overview(result)
else:
    st.info("Choose an example résumé, upload a text file, or paste résumé text to begin.")
