import streamlit as st
import sys
from pathlib import Path

# FORCE THE APP TO LOG IN OFFLINE BYPASS
st.session_state["access_token"] = "offline_authenticated"
st.session_state["user_email"] = "developer@local.com"

# Put the repo root on sys.path so the imports resolve
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure page
st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auth state initialization
for key, default in [
    ("access_token", None),
    ("refresh_token", None),
    ("user_id", None),
    ("user_email", None),
    ("auth_error", None),
    ("auth_info", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Google OAuth session exchange
if not st.session_state.access_token and "code" in st.query_params:
    from frontend.services import supabase_client
    result = supabase_client.exchange_code_for_session(st.query_params["code"])
    st.query_params.clear()
    if "error" in result:
        st.session_state.auth_error = f"Google sign-in failed: {result['error']}"
    else:
        st.session_state.access_token  = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user_id       = result["user_id"]
        st.session_state.user_email    = result["email"]
        st.rerun()

# Load custom CSS
def load_css():
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        with open(css_path, 'r') as f:
            return f'<style>{f.read()}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

# Initialize session state for view management
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()
    
    if st.button("🎯 ATS Scorer", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()
    
    if st.button("📚 Resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 👤 Account")

    from frontend.services import supabase_client

    if st.session_state.access_token:
        st.caption(f"Signed in as **{st.session_state.user_email}**")
        if st.button("Sign out", use_container_width=True):
            supabase_client.sign_out()
            for k in ("access_token", "refresh_token", "user_id", "user_email"):
                st.session_state[k] = None
            st.rerun()
    else:
        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None
        
        tab_in, tab_up = st.tabs(["Sign in", "Sign up"])
        
        # OAuth Button
        oauth = supabase_client.google_oauth_url()
        if "error" not in oauth:
            st.link_button("Continue with Google", url=oauth["url"], use_container_width=True)

# Main content area - Using direct imports to avoid circular dependency
if st.session_state.current_view == 'landing':
    from frontend.views.landing import render
    render()

elif st.session_state.current_view == 'scorer':
    from frontend.views.scorer import render
    render()

elif st.session_state.current_view == 'resources':
    from frontend.views.resources import render
    render()