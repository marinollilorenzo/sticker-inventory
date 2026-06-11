"""
auth.py – Gestione dell'autenticazione leggera tramite PIN numerico.

Utilizza st.session_state per mantenere lo stato di login tra i re-render
di Streamlit. Gli utenti e i relativi PIN sono configurati nei secrets.
"""

from __future__ import annotations

import streamlit as st


def get_users() -> dict[str, str]:
    """Recupera la mappa utenti → PIN dai secrets di Streamlit.

    La configurazione attesa in secrets.toml è:
        [users]
        NomeUtente = "1234"
        AltroUtente = "5678"

    Returns:
        Dizionario {nome_utente: pin}.
    """
    return dict(st.secrets.get("users", {}))


def init_auth_state() -> None:
    """Inizializza le chiavi di autenticazione in session_state se assenti."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""


def is_authenticated() -> bool:
    """Verifica se l'utente corrente è autenticato.

    Returns:
        True se l'utente ha superato il login con PIN.
    """
    return st.session_state.get("authenticated", False)


def get_current_user() -> str:
    """Restituisce il nome dell'utente autenticato.

    Returns:
        Nome utente corrente, o stringa vuota se non autenticato.
    """
    return st.session_state.get("current_user", "")


def login(username: str, pin: str) -> bool:
    """Tenta il login con username e PIN.

    Args:
        username: Nome dell'utente selezionato.
        pin: PIN di 4 cifre inserito dall'utente.

    Returns:
        True se il login ha successo, False altrimenti.
    """
    users = get_users()
    if username in users and users[username] == pin:
        st.session_state.authenticated = True
        st.session_state.current_user = username
        return True
    return False


def logout() -> None:
    """Esegue il logout dell'utente corrente, resettando lo stato di sessione."""
    st.session_state.authenticated = False
    st.session_state.current_user = ""


def render_login_form() -> bool:
    """Mostra il form di login e gestisce il flusso di autenticazione.

    Se l'utente è già autenticato, mostra un messaggio di benvenuto
    e il pulsante di logout nella sidebar.

    Returns:
        True se l'utente è autenticato (dopo login o già loggato).
    """
    init_auth_state()
    users = get_users()

    if not users:
        st.error("⚠️ Nessun utente configurato. Controlla il file `secrets.toml`.")
        st.stop()

    if is_authenticated():
        with st.sidebar:
            st.success(f"👤 **{get_current_user()}**")
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        return True

    # --- Form di login ---
    st.markdown("## 🔐 Accesso")
    st.markdown("Seleziona il tuo nome e inserisci il PIN per continuare.")

    user_list = sorted(users.keys())

    with st.form("login_form", clear_on_submit=True):
        selected_user = st.selectbox(
            "👤 Utente",
            options=user_list,
            index=0,
        )
        pin_input = st.text_input(
            "🔑 PIN (4 cifre)",
            type="password",
            max_chars=4,
            placeholder="••••",
        )
        submitted = st.form_submit_button("Accedi", use_container_width=True)

    if submitted:
        if not pin_input:
            st.warning("Inserisci il PIN.")
        elif login(selected_user, pin_input):
            st.rerun()
        else:
            st.error("❌ PIN errato. Riprova.")

    return False
