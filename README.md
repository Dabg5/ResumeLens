# ResumeLens
An application that processes textual résumés and determines whether the qualifications identified in a candidate's résumé satisfy patterns defined for a professional profile.

Formal language-based résumé screening (CyED3 2026-2, Integrative Task 1).
Pipeline: regex extraction -> finite-state transducers -> finite automata -> textX DSL.

## Team
- Nicolas Mejia
- Daniel Barragan
- Jacobo Rodriguez

## IDE
- PyCharm

## Run
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```
Exporting diagrams to SVG (`resumelens/viz/diagrams.py`) needs the Graphviz program installed (Windows: installer from graphviz.org or `winget install graphviz`; Linux: `sudo apt install graphviz`; macOS: `brew install graphviz`). The Streamlit app does not need it.

Deploy: Streamlit Community Cloud with Python 3.12 (Advanced settings); `packages.txt` installs graphviz.

## Layout
See `docs/01-architecture.md`.
