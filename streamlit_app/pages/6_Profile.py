import streamlit as st

st.title("👤 Profil")

if "uid" not in st.session_state:
    st.warning("Belum login.")
    st.stop()

st.write(
    "UID:",
    st.session_state.uid
)

if st.button("Logout"):

    st.session_state.clear()

    st.rerun()