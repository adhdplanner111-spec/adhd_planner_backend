import streamlit as st
import time

if "token" not in st.session_state:
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

with st.sidebar:

    st.title("🧠 ADHD Planner")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

st.markdown("""
<div style="
    padding:20px;
    border-radius:15px;
    background:linear-gradient(90deg,#EC4899,#8B5CF6);
    color:white;
">
    <h1>🎯 Focus Mode</h1>
    <p>Tingkatkan fokus Anda dengan metode Pomodoro.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

minutes = st.slider(
    "Durasi Fokus (menit)",
    1,
    60,
    25
)

if st.button("▶ Mulai Fokus"):

    total_seconds = minutes * 60

    progress = st.progress(0)

    timer_text = st.empty()

    for second in range(total_seconds):

        remaining = total_seconds - second

        mins = remaining // 60
        secs = remaining % 60

        timer_text.markdown(
            f"# ⏳ {mins:02d}:{secs:02d}"
        )

        progress.progress(
            (second + 1) / total_seconds
        )

        time.sleep(1)

    st.balloons()

    st.success(
        "🎉 Sesi fokus selesai!"
    )