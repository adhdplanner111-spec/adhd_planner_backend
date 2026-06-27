import streamlit as st
import requests
import plotly.express as px
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# =========================
# CEK LOGIN
# =========================
if "token" not in st.session_state:
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("🧠 ADHD Planner")

    st.write(
        f"UID: {st.session_state.uid[:8]}"
    )

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =========================
# HEADER
# =========================
st.markdown("""
<div style="
    padding:25px;
    border-radius:15px;
    background:linear-gradient(90deg,#7C3AED,#4F46E5);
    color:white;
">
    <h1>🧠 ADHD Planner Dashboard</h1>
    <p>Kelola tugas dan tingkatkan fokus Anda.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================
# AMBIL DATA TASK
# =========================
headers = {
    "Authorization":
        f"Bearer {st.session_state.token}"
}

response = requests.get(
    f"{API_URL}/tasks/",
    headers=headers
)

if response.status_code == 200:

    tasks = response.json()["data"]

    total_task = len(tasks)

    pending = len([
        t for t in tasks
        if t["status"] == "Pending"
    ])

    completed = len([
        t for t in tasks
        if t["status"] == "Completed"
    ])

    high_priority = len([
        t for t in tasks
        if t["priority"] == "High"
    ])

    productivity = 0

    if total_task > 0:
        productivity = int(
            completed / total_task * 100
        )

    # ======================
    # CARD STATISTIK
    # ======================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📋 Total Task",
        total_task
    )

    col2.metric(
        "⏳ Pending",
        pending
    )

    col3.metric(
        "✅ Selesai",
        completed
    )

    col4.metric(
        "🔥 Prioritas Tinggi",
        high_priority
    )

    st.divider()

    # ======================
    # PROGRESS
    # ======================
    st.subheader("📈 Produktivitas")

    st.progress(productivity / 100)

    st.write(
        f"Produktivitas: {productivity}%"
    )

    st.divider()

    # ======================
    # GRAFIK
    # ======================
    col1, col2 = st.columns(2)

    with col1:

        status_data = {
            "Status": [
                "Pending",
                "Completed"
            ],
            "Jumlah": [
                pending,
                completed
            ]
        }

        fig1 = px.pie(
            status_data,
            names="Status",
            values="Jumlah",
            title="Status Task"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with col2:

        priority_count = {}

        for task in tasks:

            priority = task["priority"]

            if priority not in priority_count:
                priority_count[priority] = 0

            priority_count[priority] += 1

        priority_data = {
            "Priority":
                list(priority_count.keys()),
            "Jumlah":
                list(priority_count.values())
        }

        fig2 = px.bar(
            priority_data,
            x="Priority",
            y="Jumlah",
            title="Prioritas Task"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # ======================
    # DEADLINE TASK
    # ======================
    st.subheader("📅 Daftar Deadline")

    data = []

    for task in tasks:

        data.append({
            "Task": task["title"],
            "Priority": task["priority"],
            "Status": task["status"],
            "Deadline": task["due_date"]
        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True
    )

else:
    st.error(
        "Gagal mengambil data task."
    )