# ResumeLens

ResumeLens processes plain-text resumes and checks whether their extracted qualifications match the formal pattern of a professional profile. It reports acceptance, a recognition trace, and missing required categories; it does not rank candidates.

Formal-language-based resume screening for CyED3 2026-2, Integrative Task 1.

## Team

- Nicolas Mejia
- Daniel Barragan
- Jacobo Rodriguez

## Requirements

- Python 3.12
- Graphviz is needed only to export automaton diagrams from `resumelens/viz/diagrams.py`. The Streamlit app itself does not require the local Graphviz executable.

## Run locally

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

### macOS or Linux

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

## Deploy to Streamlit Community Cloud

Create an app from the `Dabg5/ResumeLens` GitHub repository, using the `main` branch and `app.py` as the entrypoint. In Advanced settings, select Python 3.12. The root `requirements.txt` installs Python packages, and `packages.txt` installs the Graphviz system package.

**Live app:** Pending deployment.

## Project documentation

- [Architecture](docs/01-architecture.md)
- [Automata and classification](docs/02b-automata.md)
- [Test cases](docs/03-test-cases.md)
- [Research review](docs/04-literature-review.md)
