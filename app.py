"""
app.py – Entry point dell'applicazione Streamlit.

Gestore Inventario Figurine: web app mobile-first per la gestione
di un inventario di figurine/collezionabili condiviso tra più utenti.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from auth import get_current_user, render_login_form
from database import (
    decrement_stickers,
    delete_stickers,
    get_all_editions,
    get_all_owners,
    get_inventory,
    search_stickers,
    upsert_stickers,
)
from utils import format_sticker_list, parse_sticker_list, parse_sticker_list_with_counts

# ─── Configurazione Pagina ───────────────────────────────────────────────────

st.set_page_config(
    page_title="📇 Inventario Figurine",
    page_icon="📇",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Stile CSS per mobile-first ──────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Mobile-first: spaziatura e font ottimizzati */
    .stApp {
        max-width: 700px;
        margin: 0 auto;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 16px !important;  /* Previene zoom su iOS */
    }
    .stButton > button {
        font-size: 16px !important;
        padding: 0.6rem 1rem !important;
    }
    /* Tab styling mobile-friendly */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Header ──────────────────────────────────────────────────────────────────

st.title("📇 Inventario Figurine")
st.caption("Gestisci la tua collezione e controlla le mancoliste in un tap.")

# ─── Autenticazione ──────────────────────────────────────────────────────────

if not render_login_form():
    st.stop()

# ─── Navigazione a Tab ───────────────────────────────────────────────────────

tab_search, tab_inventory, tab_manage = st.tabs(
    ["🔍 Mancolista", "📋 Inventario", "✏️ Gestione"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: Ricerca Mancolista
# ═══════════════════════════════════════════════════════════════════════════════

with tab_search:
    st.subheader("🔍 Controlla Mancolista")
    st.markdown(
        "Incolla i codici delle figurine cercate (separati da virgola) "
        "per vedere quali sono disponibili nell'inventario."
    )

    # Selettori
    editions = get_all_editions()
    owners = get_all_owners()

    if not editions:
        st.info("📭 Nessuna edizione presente nel database. Aggiungi figurine dalla tab **Gestione**.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            search_edition = st.selectbox(
                "📚 Edizione",
                options=editions,
                key="search_edition",
            )
        with col2:
            search_owner = st.selectbox(
                "👤 Proprietario",
                options=owners,
                key="search_owner",
            )

        # Input mancolista
        raw_input = st.text_area(
            "📝 Codici figurine (separati da virgola)",
            placeholder="Es: 105, 120, ITA04, 250, 301",
            key="search_input",
            height=120,
        )

        if st.button("🔎 Cerca", width="stretch", key="btn_search"):
            codes = parse_sticker_list(raw_input)

            if not codes:
                st.warning("Inserisci almeno un codice figurina.")
            else:
                found = search_stickers(search_edition, search_owner, codes)
                found_codes = {row["sticker_code"] for row in found}
                not_found = [c for c in codes if c not in found_codes]

                # Salva in session_state per azione rapida
                st.session_state.search_results = found
                st.session_state.search_edition = search_edition
                st.session_state.search_owner = search_owner

                # Risultati
                if found:
                    st.success(f"✅ **{len(found)}** figurine trovate su {len(codes)} cercate!")
                    df_found = pd.DataFrame(found)
                    df_found.columns = ["Codice", "Quantità"]
                    st.dataframe(df_found, width="stretch", hide_index=True)
                else:
                    st.info("Nessuna delle figurine cercate è presente nell'inventario.")

                if not_found:
                    st.markdown(
                        f"❌ **Non trovate** ({len(not_found)}): "
                        f"`{format_sticker_list(not_found)}`"
                    )

        # Azione rapida: Segna come vendute/scambiate
        if "search_results" in st.session_state and st.session_state.search_results:
            st.divider()
            results = st.session_state.search_results

            st.markdown(f"**{len(results)} figurine** pronte per essere segnate come vendute/scambiate.")

            if st.button(
                "📤 Segna Trovate come Vendute (-1)",
                width="stretch",
                type="primary",
                key="btn_decrement",
            ):
                codes_to_dec = [r["sticker_code"] for r in results]
                updated, deleted = decrement_stickers(
                    st.session_state.search_edition,
                    st.session_state.search_owner,
                    codes_to_dec,
                )
                st.success(
                    f"✅ Operazione completata! "
                    f"Aggiornate: {updated} | Rimosse (qty→0): {deleted}"
                )
                # Pulisci risultati
                del st.session_state.search_results


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: Inventario Completo
# ═══════════════════════════════════════════════════════════════════════════════

with tab_inventory:
    st.subheader("📋 Inventario Completo")

    # Filtri
    all_editions = ["Tutte"] + get_all_editions()
    all_owners = ["Tutti"] + get_all_owners()

    col1, col2 = st.columns(2)
    with col1:
        filter_edition = st.selectbox(
            "📚 Filtra Edizione",
            options=all_editions,
            key="inv_edition",
        )
    with col2:
        filter_owner = st.selectbox(
            "👤 Filtra Proprietario",
            options=all_owners,
            key="inv_owner",
        )

    # Recupera dati
    edition_filter = None if filter_edition == "Tutte" else filter_edition
    owner_filter = None if filter_owner == "Tutti" else filter_owner

    inventory_data = get_inventory(edition=edition_filter, owner=owner_filter)

    if inventory_data:
        df = pd.DataFrame(inventory_data)
        # Rinomina colonne per l'utente
        display_cols = {
            "edition": "Edizione",
            "sticker_code": "Codice",
            "quantity": "Quantità",
            "owner": "Proprietario",
        }
        df_display = df.rename(columns=display_cols)

        # Mostra solo le colonne utili
        cols_to_show = [v for v in display_cols.values() if v in df_display.columns]
        df_display = df_display[cols_to_show]

        st.dataframe(df_display, width="stretch", hide_index=True)
        st.caption(f"📊 Totale righe: **{len(df_display)}**")

        # Download CSV
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Scarica CSV",
            data=csv,
            file_name="inventario_figurine.csv",
            mime="text/csv",
            width="stretch",
        )
    else:
        st.info("📭 Nessuna figurina trovata con i filtri selezionati.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Gestione Manuale
# ═══════════════════════════════════════════════════════════════════════════════

with tab_manage:
    st.subheader("✏️ Gestione Manuale")

    current_user = get_current_user()

    # ─── Sezione: Aggiungi Figurine ──────────────────────────────────────────

    st.markdown("### ➕ Aggiungi Figurine")

    with st.form("add_form", clear_on_submit=True):
        add_edition = st.text_input(
            "📚 Edizione",
            placeholder="Es: Panini 2014-2015",
        )
        add_codes_raw = st.text_area(
            "📝 Codici figurine (separati da virgola)",
            placeholder="Es: 105, 120, ITA04",
            height=100,
        )
        add_quantity = st.number_input(
            "🔢 Quantità per ciascuna",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
        )
        add_submitted = st.form_submit_button(
            "➕ Aggiungi all'inventario",
            width="stretch",
        )

    if add_submitted:
        if not add_edition.strip():
            st.warning("Inserisci il nome dell'edizione.")
        elif not add_codes_raw.strip():
            st.warning("Inserisci almeno un codice figurina.")
        else:
            counts = parse_sticker_list_with_counts(add_codes_raw)
            # Moltiplica per la quantità specificata nel selettore numerico
            final_counts = {k: v * add_quantity for k, v in counts.items()}
            
            edition_clean = add_edition.strip()
            processed = upsert_stickers(
                edition=edition_clean,
                owner=current_user,
                sticker_counts=final_counts,
            )
            st.success(
                f"✅ **{processed}** figurine aggiunte/aggiornate "
                f"nell'edizione *{edition_clean}* per **{current_user}**."
            )

    st.divider()

    # ─── Sezione: Rimuovi Figurine ───────────────────────────────────────────

    st.markdown("### 🗑️ Rimuovi Figurine")

    with st.form("remove_form", clear_on_submit=True):
        # Edizioni disponibili per l'utente corrente
        user_editions = get_all_editions()

        if user_editions:
            remove_edition = st.selectbox(
                "📚 Edizione",
                options=user_editions,
                key="remove_edition",
            )
        else:
            remove_edition = st.text_input(
                "📚 Edizione",
                placeholder="Es: Panini 2014-2015",
                key="remove_edition_input",
            )

        remove_codes_raw = st.text_area(
            "📝 Codici figurine da rimuovere (separati da virgola)",
            placeholder="Es: 105, 120",
            height=100,
        )
        remove_submitted = st.form_submit_button(
            "🗑️ Rimuovi dall'inventario",
            width="stretch",
            type="primary",
        )

    if remove_submitted:
        if not remove_codes_raw.strip():
            st.warning("Inserisci almeno un codice figurina.")
        else:
            codes = parse_sticker_list(remove_codes_raw)
            edition_val = remove_edition if isinstance(remove_edition, str) else ""
            if not edition_val.strip():
                st.warning("Seleziona o inserisci un'edizione.")
            else:
                deleted = delete_stickers(
                    edition=edition_val.strip(),
                    owner=current_user,
                    sticker_codes=codes,
                )
                st.success(
                    f"🗑️ **{deleted}** figurine rimosse "
                    f"dall'edizione *{edition_val.strip()}* per **{current_user}**."
                )
