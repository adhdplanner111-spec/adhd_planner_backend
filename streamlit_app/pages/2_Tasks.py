import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# ======================
# CEK LOGIN
# ======================
if "token" not in st.session_state:
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

# ======================
# SIDEBAR
# ======================
with st.sidebar:

    st.title("🧠 ADHD Planner")

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# ======================
# HEADER
# ======================
st.markdown("""
<div style="
    padding:20px;
    border-radius:15px;
    background:linear-gradient(90deg,#7C3AED,#4F46E5);
    color:white;
">
    <h1>📋 My Tasks</h1>
    <p>Kelola tugas dan tingkatkan produktivitas Anda.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

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

    if len(tasks) == 0:
        st.info("Belum ada task.")
        st.stop()

    for task in tasks:

        # warna prioritas
        color = "#22c55e"

        if task["priority"] == "High":
            color = "#ef4444"

        elif task["priority"] == "Medium":
            color = "#f59e0b"

        with st.container(border=True):

            st.markdown(
                f"""
                <div style="
                    border-left:8px solid {color};
                    padding-left:15px;
                ">
                    <h3>{task['title']}</h3>
                    <p>{task['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            col1.info(
                f"Priority: {task['priority']}"
            )

            col2.success(
                f"Status: {task['status']}"
            )

            st.write(
                f"📅 Deadline: {task['due_date']}"
            )

            col1, col2 = st.columns(2)

            # Selesai
            if col1.button(
                "✅ Selesai",
                key=f"done_{task['task_id']}"
            ):

                requests.put(
                    f"{API_URL}/tasks/{task['task_id']}",
                    headers=headers,
                    json={
                        "status": "Completed"
                    }
                )

                st.rerun()

            # Hapus
            if col2.button(
                "🗑 Hapus",
                key=f"delete_{task['task_id']}"
            ):

                requests.delete(
                    f"{API_URL}/tasks/{task['task_id']}",
                    headers=headers
                )

                st.rerun()

else:
    st.error("Gagal mengambil data.")