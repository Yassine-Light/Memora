"""Pipeline 2 - Supervisor (caregiver) dashboard.

Run from the repo root:
    streamlit run src/interfaces/supervisor_ui.py --server.port 8501

Rules:
  * The first person to sign up becomes the owner. Sign-up is then closed.
  * Only the owner can add or remove other supervisors.
  * Any logged-in supervisor can edit the patient profile and events.
"""
import re
import sys
from datetime import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.interfaces import common as db  # noqa: E402

db.safe_page_config(page_title="MemoryAnchor - Supervisor", page_icon="⚓", layout="centered")

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
MARITAL = {"Single": "single", "Married": "married", "Widowed": "widowed", "Divorced": "divorced"}
EVENT_TYPES = {"Medicine": "medicine", "Food": "food", "Trip / activity": "date"}
EVENT_LABELS = {v: k for k, v in EVENT_TYPES.items()}


# ---------- helpers ----------
def check_credentials(username: str, password: str) -> str | None:
    """Return an error message, or None if the credentials are acceptable."""
    if not USERNAME_RE.match(username.strip()):
        return "Username must be 3-32 characters: letters, numbers, . _ -"
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None


def build_situation(status: str, spouse: str) -> str:
    """Human-readable sentence stored in `situation` (read by the AI prompt)."""
    spouse = spouse.strip()
    if status == "married":
        return f"Married to {spouse}"
    if status == "widowed":
        return f"Widowed; the late spouse was named {spouse}" if spouse else "Widowed"
    return status.capitalize()


def logout():
    st.session_state.pop("user", None)


# ---------- screens ----------
def screen_setup():
    st.title("Create the owner account")
    st.write("This is the first account on this system. It will be the owner and can add other supervisors. "
             "Sign-up closes as soon as it is created.")
    with st.form("setup"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        go = st.form_submit_button("Create owner account", type="primary")
    if not go:
        return
    err = check_credentials(username, password)
    if not err and password != confirm:
        err = "Passwords do not match."
    if err:
        st.error(err)
        return
    with db.lock:  # blocks two simultaneous first sign-ups
        if db.load_supervisors():
            st.error("Sign-up is closed. Ask the account owner to add you.")
            return
        db.save_supervisors([db.make_user(username.strip(), password, is_owner=True)])
    st.session_state["user"] = {"username": username.strip(), "is_owner": True}
    st.rerun()


def screen_login():
    st.title("Supervisor login")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        go = st.form_submit_button("Log in", type="primary")
    if not go:
        return
    user = db.find_user(username)
    if not user or not db.check_password(user, password):
        st.error("Wrong username or password.")
        return
    st.session_state["user"] = {"username": user["username"], "is_owner": user["is_owner"]}
    st.rerun()


def tab_patient():
    data = db.load_patient()
    p = data["patient"]
    st.subheader("Patient profile")
    name = st.text_input("Patient name", value=p.get("name", ""))
    try:
        saved_age = min(max(int(p.get("age") or 0), 0), 130)
    except (TypeError, ValueError):
        saved_age = 0
    age = st.number_input("Age", min_value=0, max_value=130, value=saved_age, step=1)
    labels = list(MARITAL)
    current = next((k for k, v in MARITAL.items() if v == p.get("marital_status")), "Single")
    status_label = st.selectbox("Marital status", labels, index=labels.index(current))
    status = MARITAL[status_label]
    spouse = ""
    if status in ("married", "widowed"):
        spouse = st.text_input("Spouse's name", value=p.get("spouse_name", ""))
    profession = st.text_input("Job", value=p.get("profession", ""))
    family = st.text_area("Family members (one per line, e.g. \"Sara (daughter)\")",
                          value="\n".join(p.get("family", [])), height=120)
    hobby = st.text_input("Hobbies and favourite things", value=p.get("hobby", ""))

    if st.button("Save patient", type="primary"):
        if not name.strip():
            st.error("Patient name is required.")
        elif status == "married" and not spouse.strip():
            st.error("Enter the spouse's name for a married patient.")
        else:
            data["patient"] = {
                **p,  # keep any extra keys teammates added
                "name": name.strip(),
                "age": int(age),
                "marital_status": status,
                "spouse_name": spouse.strip(),
                "situation": build_situation(status, spouse),
                "profession": profession.strip(),
                "family": [f.strip() for f in family.splitlines() if f.strip()],
                "hobby": hobby.strip(),
            }
            db.save_patient(data)
            st.success("Patient saved.")


def remove_event(time_str: str, description: str):
    """Button callback: runs before the page redraws, so the list is already up to date."""
    data = db.load_patient()
    data["events"] = [e for e in data["events"] if not (e["time"] == time_str and e["description"] == description)]
    db.save_patient(data)


def tab_events():
    st.subheader("Events to remind the patient about")
    with st.form("add_event", clear_on_submit=True):
        c1, c2 = st.columns(2)
        when = c1.time_input("Time", value=time(8, 0), step=60)
        kind = c2.selectbox("Type", list(EVENT_TYPES))
        desc = st.text_input("Description", placeholder="e.g. Take the diabetes pill with breakfast")
        add = st.form_submit_button("Add event", type="primary")

    data = db.load_patient()
    if add:
        if not desc.strip():
            st.error("Write a short description of the event.")
        else:
            data["events"].append({
                "time": when.strftime("%H:%M"),
                "event_type": EVENT_TYPES[kind],
                "description": desc.strip(),
            })
            data["events"].sort(key=lambda e: e["time"])
            db.save_patient(data)
            st.success("Event added.")

    st.markdown("#### Scheduled events")
    if not data["events"]:
        st.info("No events yet. Add the first one above.")
    for i, e in enumerate(data["events"]):
        c1, c2, c3 = st.columns([1, 5, 1.4], vertical_alignment="center")
        c1.markdown(f"**{e['time']}**")
        c2.markdown(f"{EVENT_LABELS.get(e['event_type'], 'Activity')}: {e['description']}")
        c3.button("Remove", key=f"rm_{i}_{e['time']}", on_click=remove_event, args=(e["time"], e["description"]))


def tab_supervisors(me: dict):
    st.subheader("Supervisors")
    users = db.load_supervisors()
    st.dataframe(
        [{"Username": u["username"], "Role": "Owner" if u["is_owner"] else "Supervisor"} for u in users],
        hide_index=True,
    )
    with st.form("add_supervisor", clear_on_submit=True):
        st.write("Add a supervisor")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        go = st.form_submit_button("Add supervisor", type="primary")
    if go:
        err = check_credentials(username, password)
        with db.lock:
            users = db.load_supervisors()
            if not err and any(u["username"].lower() == username.strip().lower() for u in users):
                err = "That username is already taken."
            if err:
                st.error(err)
            else:
                users.append(db.make_user(username.strip(), password, is_owner=False))
                db.save_supervisors(users)
                st.success(f"Added {username.strip()}.")
                st.rerun()

    removable = [u["username"] for u in users if not u["is_owner"]]
    if removable:
        who = st.selectbox("Remove a supervisor", removable, index=None, placeholder="Choose a supervisor")
        if who and st.button(f"Remove {who}"):
            with db.lock:
                db.save_supervisors([u for u in db.load_supervisors() if u["username"] != who])
            st.rerun()


def screen_dashboard(me: dict):
    with st.sidebar:
        st.write(f"Signed in as **{me['username']}**" + (" (owner)" if me["is_owner"] else ""))
        st.button("Log out", on_click=logout)
    st.title("MemoryAnchor")
    names = ["Patient", "Events"] + (["Supervisors"] if me["is_owner"] else [])
    tabs = st.tabs(names)
    with tabs[0]:
        tab_patient()
    with tabs[1]:
        tab_events()
    if me["is_owner"]:
        with tabs[2]:
            tab_supervisors(me)


# ---------- router ----------
if not db.load_supervisors():
    screen_setup()
elif "user" in st.session_state and not db.find_user(st.session_state["user"]["username"]):
    logout()  # account was removed by the owner
    st.rerun()
elif "user" not in st.session_state:
    screen_login()
else:
    screen_dashboard(st.session_state["user"])

st.markdown("[← Back to the patient screen](/)")