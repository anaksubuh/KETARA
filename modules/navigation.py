import streamlit as st

def switch_page_with_token(page_name: str):
    """Pindah halaman dengan membawa token"""
    if st.session_state.get('logged_in', False) and st.session_state.token:
        # Simpan token ke session_state sebelum pindah
        st.session_state._navigation_token = st.session_state.token
        st.switch_page(page_name)
    else:
        st.switch_page(page_name)

def check_navigation_token():
    """Cek apakah ada token dari navigasi sebelumnya"""
    if st.session_state.get('_navigation_token'):
        token = st.session_state._navigation_token
        st.query_params["token"] = token
        del st.session_state._navigation_token
        return True
    return False