"""Single entry point for both interfaces.

Run from the repo root:
    streamlit run src/interfaces/app.py

    /            -> patient screen (default)
    /supervisor  -> supervisor login / dashboard
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
here = Path(__file__).parent
pages = [
    st.Page(str(here / "patient_ui.py"), title="Patient", default=True),
    st.Page(str(here / "supervisor_ui.py"), title="Supervisor", url_path="supervisor"),
]
st.navigation(pages, position="hidden").run()