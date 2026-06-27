import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

if "token" in st.session_state:
    st.success("Anda sudah login.")
    st.stop()

st.markdown("""
<div style="
    text-align:center;
    padding:30px;
">
    <h1>🧠 ADHD Planner</h1>
    <p>Kelola fokus dan produktivitas Anda.</p>
</div>
""", unsafe_allow_html=True)

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login"):

    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    if response.status_code == 200:

        data = response.json()

        st.session_state.token = (
            data["access_token"]
        )

        st.session_state.uid = (
            data["uid"]
        )

        st.success("Login berhasil!")

        st.rerun()

    else:
        st.error(
            response.json()["detail"]
        )