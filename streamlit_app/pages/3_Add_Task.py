import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.warning("Silakan login.")
    st.stop()

st.title("➕ Tambah Task")

with st.form("task_form"):

    title = st.text_input("Judul Task")

    description = st.text_area(
        "Deskripsi"
    )

    priority = st.selectbox(
        "Prioritas",
        ["Low", "Medium", "High"]
    )

    due_date = st.date_input(
        "Deadline"
    )

    submit = st.form_submit_button(
        "Simpan"
    )

if submit:

    headers = {
        "Authorization":
            f"Bearer {st.session_state.token}"
    }

    response = requests.post(
        f"{API_URL}/tasks/",
        headers=headers,
        json={
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": str(due_date)
        }
    )

    if response.status_code == 200:
        st.success("Task berhasil dibuat.")
        st.rerun()

    else:
        st.error(response.text)