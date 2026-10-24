"""Pipeline 1 - Patient interface (the always-on ambient screen).

Open it at "/" (streamlit run src/interfaces/app.py).

This page is deliberately bare: no login, no links to the supervisor side.
Loading it also signs any supervisor out of this browser session.
Recorded audio is passed straight to the backend; there is NO fallback, so until
the STT / Gemma / TTS modules exist the page shows the backend's error.
"""
import hashlib
import html
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.interfaces import common as db  # noqa: E402

db.safe_page_config(page_title="MemoryAnchor", page_icon="⚓", layout="wide")
st.session_state.pop("user", None)  # a supervisor who lands here is logged out

TYPES = {
    "medicine": ("Medicine", "#a33a5e"),
    "food": ("Mealtime", "#9a6212"),
    "date": ("Activity", "#26705f"),
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap');
    :root{--bg:#f3f6f8;--surface:#ffffff;--ink:#14212b;--muted:#586774;--line:#d8e0e6;--blue:#2b5c8a;--onblue:#ffffff}
    @media (prefers-color-scheme: dark){
      :root{--bg:#0f1a22;--surface:#17252f;--ink:#e8eff3;--muted:#9db0bc;--line:#2a3c48;--blue:#6fa8dc;--onblue:#0f1a22}
    }
    .stApp{background:var(--bg)}
    [data-testid="stHeader"], footer, #MainMenu{display:none !important}
    .block-container{max-width:1240px;padding:2.4rem 2rem 3rem !important}
    .ma, .ma *{font-family:'Atkinson Hyperlegible',Verdana,Tahoma,sans-serif !important;color:var(--ink)}

    .ma.head{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap;margin-bottom:28px}
    .ma .hello{font-size:30px;color:var(--muted)}
    .ma .name{font-size:68px;font-weight:700;line-height:1.05}
    .ma .clock{text-align:right}
    .ma .time{font-size:76px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
    .ma .day{font-size:26px;color:var(--muted);margin-top:6px}

    .ma.next{background:var(--c);border-radius:28px;padding:34px 38px;margin-bottom:30px}
    .ma.next *{color:#fff}
    .ma.next .kind{font-size:28px;font-weight:700;opacity:.92}
    .ma.next .what{font-size:46px;font-weight:700;line-height:1.2;margin:10px 0 22px}
    .ma.next .at{font-size:64px;font-weight:700;font-variant-numeric:tabular-nums}
    .ma.next .in{font-size:28px;margin-inline-start:18px;opacity:.92}

    .ma h3{font-size:28px;font-weight:700;color:var(--muted);margin:26px 0 12px}
    .ma .item{display:grid;grid-template-columns:92px 1fr;gap:18px;align-items:center;background:var(--surface);
      border:2px solid var(--line);border-left:10px solid var(--c);border-radius:18px;padding:16px 20px;margin-bottom:12px}
    .ma .item .t{font-size:32px;font-weight:700;font-variant-numeric:tabular-nums}
    .ma .item .k{font-size:20px;color:var(--muted)}
    .ma .item .d{font-size:28px;line-height:1.3}
    .ma .item.done{opacity:.55;border-left-color:var(--line)}
    .ma .item.done .k::after{content:" - done"}
    .ma .quiet{font-size:32px;line-height:1.4;background:var(--surface);border:2px solid var(--line);border-radius:22px;padding:30px}

    .st-key-talk{background:var(--surface);border:2px solid var(--line);border-radius:28px;padding:2rem !important}
    .ma .talk-h{font-size:44px;font-weight:700;line-height:1.1}
    .ma .talk-p{font-size:24px;color:var(--muted);margin:10px 0 6px;line-height:1.4}
    .ma .try{font-size:22px;color:var(--muted);margin-top:14px}
    .ma .bubble{font-size:26px;line-height:1.45;padding:16px 22px;border-radius:20px;margin-top:14px;max-width:92%}
    .ma .bubble.you{background:var(--bg);margin-inline-start:auto}
    .ma .bubble.ai{background:var(--blue)}
    .ma .bubble.ai, .ma .bubble.ai *{color:var(--onblue)}
    .ma .problem{font-size:24px;line-height:1.4;margin-top:14px;padding:16px 20px;border-radius:16px;border:2px solid #a33a5e}
    .ma .dev{font-size:15px;color:var(--muted);margin-top:8px;word-break:break-word}
    </style>
    """,
    unsafe_allow_html=True,
)


def minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def in_words(diff: int) -> str:
    if diff <= 0:
        return "now"
    h, m = divmod(diff, 60)
    parts = ([f"{h} hour{'s' if h != 1 else ''}"] if h else []) + ([f"{m} minute{'s' if m != 1 else ''}"] if m else [])
    return "in " + " and ".join(parts)


def greeting(hour: int) -> str:
    return "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"


@st.fragment(run_every="15s")
def header():
    now = datetime.now()
    st.markdown(
        f"<div class='ma head'><div><div class='hello'>{greeting(now.hour)}</div>"
        f"<div class='clock'><div class='time'>{now:%H:%M}</div><div class='day'>{now:%A, %d %B}</div></div></div>",
        unsafe_allow_html=True,
    )


def item(e: dict, css: str = "") -> str:
    label, color = TYPES.get(e["event_type"], TYPES["date"])
    return (f"<div class='item {css}' style='--c:{color}'><div class='t'>{e['time']}</div>"
            f"<div><div class='k'>{label}</div><div class='d'>{html.escape(e['description'])}</div></div></div>")


@st.fragment(run_every="15s")
def events():
    """Re-reads patient.json every 15 s so supervisor changes appear without a refresh."""
    now_dt = datetime.now()
    now = now_dt.hour * 60 + now_dt.minute
    evs = sorted(db.load_patient()["events"], key=lambda e: e["time"])
    if not evs:
        st.markdown("<div class='ma quiet'>Nothing is planned for today. Enjoy a quiet day.</div>", unsafe_allow_html=True)
        return

    done = [e for e in evs if minutes(e["time"]) < now]
    later = [e for e in evs if minutes(e["time"]) >= now]
    nxt = later[0] if later else evs[0]
    tomorrow = not later
    diff = minutes(nxt["time"]) + (1440 if tomorrow else 0) - now
    label, color = TYPES.get(nxt["event_type"], TYPES["date"])

    out = (
        f"<div class='ma next' style='--c:{color}'>"
        f"<div class='kind'>{'Tomorrow: ' if tomorrow else 'Next: '}{label}</div>"
        f"<div class='what'>{html.escape(nxt['description'])}</div>"
        f"<span class='at'>{nxt['time']}</span><span class='in'>{in_words(diff)}</span></div>"
    )
    rest = later[1:] if later else []
    if rest:
        out += "<div class='ma'><h3>Later today</h3>" + "".join(item(e) for e in rest) + "</div>"
    if done:
        out += "<div class='ma'><h3>Earlier today</h3>" + "".join(item(e, "done") for e in done) + "</div>"
    st.markdown(out, unsafe_allow_html=True)


def talk_to_backend(audio_bytes: bytes) -> dict:
    """Hand the recording to the backend. No fallback: errors propagate to the caller.

    Expected (adjust the import/name here if your teammates choose differently):
        src.core.orchestrator.handle_patient_audio(audio_bytes: bytes) -> dict with
            "transcript": str, "reply_text": str, "reply_audio": bytes | None
    """
    from src.core.orchestrator import handle_patient_audio

    return handle_patient_audio(audio_bytes)


def talk_panel():
    with st.container(key="talk"):
        st.markdown(
            "<div class='ma'><div class='talk-h'>Talk to me</div>"
            "<div class='talk-p'>Press the microphone, say what you like, then press it again.</div></div>",
            unsafe_allow_html=True,
        )
        audio = st.audio_input("Record your voice", label_visibility="collapsed")
        st.markdown(
            "<div class='ma try'>You can ask: &ldquo;What do I do next?&rdquo; or &ldquo;Who is coming today?&rdquo;</div>",
            unsafe_allow_html=True,
        )
        chat = st.session_state.setdefault("chat", [])

        if audio is not None:
            raw = audio.getvalue()
            digest = hashlib.sha256(raw).hexdigest()
            if st.session_state.get("last_audio") != digest:  # process each recording once
                st.session_state["last_audio"] = digest
                with st.spinner("Thinking..."):
                    try:
                        result = talk_to_backend(raw)
                    except Exception as exc:  # shown as-is so teammates see NotImplementedError etc.
                        st.session_state["backend_error"] = f"{type(exc).__name__}: {exc}"
                    else:
                        st.session_state.pop("backend_error", None)
                        chat.append(("you", result.get("transcript", "")))
                        chat.append(("ai", result.get("reply_text", "")))
                        st.session_state["reply_audio"] = result.get("reply_audio")

        if err := st.session_state.get("backend_error"):
            st.markdown(
                "<div class='ma problem'>I can't answer right now. Please ask someone nearby for help."
                f"<div class='dev'>Developer details: {html.escape(err)}</div></div>",
                unsafe_allow_html=True,
            )
        if reply_audio := st.session_state.pop("reply_audio", None):
            st.audio(reply_audio, autoplay=True)  # popped so it plays once, not on every rerun
        bubbles = "".join(
            f"<div class='bubble {who}'>{html.escape(text)}</div>" for who, text in reversed(chat[-6:]) if text
        )
        if bubbles:
            st.markdown(f"<div class='ma'>{bubbles}</div>", unsafe_allow_html=True)


header()
left, right = st.columns([1.35, 1], gap="large")
with left:
    events()
with right:
    talk_panel()