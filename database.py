"""
database.py – Gestione della connessione Supabase e operazioni CRUD.

Centralizza tutte le interazioni con il database PostgreSQL ospitato su Supabase,
fornendo un'interfaccia pulita e type-safe per le operazioni sull'inventario.
"""

from __future__ import annotations

from typing import Any

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_supabase_client() -> Client:
    """Crea e restituisce un client Supabase singleton (cachato da Streamlit).

    Le credenziali sono lette dai secrets di Streamlit:
        [supabase]
        url = "https://xxxxx.supabase.co"
        key = "eyJ..."

    Returns:
        Istanza del client Supabase pronta all'uso.

    Raises:
        KeyError: Se i secrets non sono configurati correttamente.
    """
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["key"]
    return create_client(url, key)


def get_all_editions() -> list[str]:
    """Recupera la lista di tutte le edizioni distinte presenti nel database.

    Returns:
        Lista ordinata di nomi di edizione.
    """
    client = get_supabase_client()
    response = client.table("inventory").select("edition").execute()

    editions: set[str] = {row["edition"] for row in response.data if row.get("edition")}
    return sorted(editions)


def get_all_owners() -> list[str]:
    """Recupera la lista di tutti i proprietari distinti presenti nel database.

    Returns:
        Lista ordinata di nomi di proprietario.
    """
    client = get_supabase_client()
    response = client.table("inventory").select("owner").execute()

    owners: set[str] = {row["owner"] for row in response.data if row.get("owner")}
    return sorted(owners)


def search_stickers(
    edition: str,
    owner: str,
    sticker_codes: list[str],
) -> list[dict[str, Any]]:
    """Cerca figurine specifiche nel database per un proprietario e un'edizione.

    Utilizza set intersection per filtrare i risultati in modo efficiente O(1).

    Args:
        edition: Nome dell'edizione da filtrare.
        owner: Nome del proprietario.
        sticker_codes: Lista di codici figurine da cercare.

    Returns:
        Lista di dizionari con le figurine trovate (sticker_code, quantity).
    """
    if not sticker_codes:
        return []

    client = get_supabase_client()

    # Query filtrata per edizione e proprietario
    response = (
        client.table("inventory")
        .select("sticker_code, quantity")
        .eq("edition", edition)
        .eq("owner", owner)
        .execute()
    )

    # Set intersection per lookup O(1)
    search_set = set(sticker_codes)
    found: list[dict[str, Any]] = [
        row for row in response.data
        if row.get("sticker_code") in search_set
    ]

    return found


def decrement_stickers(
    edition: str,
    owner: str,
    sticker_codes: list[str],
) -> tuple[int, int]:
    """Scala di -1 la quantità delle figurine specificate.

    Se la quantità raggiunge zero, la riga viene eliminata.

    Args:
        edition: Nome dell'edizione.
        owner: Nome del proprietario.
        sticker_codes: Lista di codici figurine da decrementare.

    Returns:
        Tupla (aggiornate, eliminate) con i conteggi delle operazioni.
    """
    client = get_supabase_client()
    updated_count = 0
    deleted_count = 0

    for code in sticker_codes:
        # Recupera la riga corrente
        response = (
            client.table("inventory")
            .select("id, quantity")
            .eq("edition", edition)
            .eq("owner", owner)
            .eq("sticker_code", code)
            .execute()
        )

        if not response.data:
            continue

        row = response.data[0]
        new_qty = row["quantity"] - 1

        if new_qty <= 0:
            # Elimina la riga se quantità arriva a zero o sotto
            client.table("inventory").delete().eq("id", row["id"]).execute()
            deleted_count += 1
        else:
            # Aggiorna la quantità
            client.table("inventory").update({"quantity": new_qty}).eq("id", row["id"]).execute()
            updated_count += 1

    return updated_count, deleted_count


def get_inventory(
    edition: str | None = None,
    owner: str | None = None,
) -> list[dict[str, Any]]:
    """Recupera l'inventario completo, con filtri opzionali.

    Args:
        edition: Se specificato, filtra per edizione.
        owner: Se specificato, filtra per proprietario.

    Returns:
        Lista di dizionari rappresentanti le righe dell'inventario.
    """
    client = get_supabase_client()
    query = client.table("inventory").select("*").order("edition").order("sticker_code")

    if edition:
        query = query.eq("edition", edition)
    if owner:
        query = query.eq("owner", owner)

    response = query.execute()
    return response.data


def upsert_stickers(
    edition: str,
    owner: str,
    sticker_counts: dict[str, int],
) -> int:
    """Inserisce o aggiorna figurine nel database (upsert).

    Se una figurina esiste già (stessa edizione + codice + proprietario),
    la quantità viene sommata a quella esistente.

    Args:
        edition: Nome dell'edizione.
        owner: Nome del proprietario.
        sticker_counts: Dizionario {codice_figurina: quantita_da_aggiungere}.

    Returns:
        Numero di figurine processate.
    """
    client = get_supabase_client()
    processed = 0

    for code, qty in sticker_counts.items():
        # Controlla se esiste già
        response = (
            client.table("inventory")
            .select("id, quantity")
            .eq("edition", edition)
            .eq("owner", owner)
            .eq("sticker_code", code)
            .execute()
        )

        if response.data:
            # Aggiorna quantità esistente
            row = response.data[0]
            new_qty = row["quantity"] + qty
            client.table("inventory").update({"quantity": new_qty}).eq("id", row["id"]).execute()
        else:
            # Inserisci nuova riga
            client.table("inventory").insert({
                "edition": edition,
                "sticker_code": code,
                "quantity": qty,
                "owner": owner,
            }).execute()

        processed += 1

    return processed


def delete_stickers(
    edition: str,
    owner: str,
    sticker_codes: list[str],
) -> int:
    """Elimina completamente figurine specifiche dal database.

    Args:
        edition: Nome dell'edizione.
        owner: Nome del proprietario.
        sticker_codes: Lista di codici figurine da eliminare.

    Returns:
        Numero di figurine eliminate.
    """
    client = get_supabase_client()
    deleted = 0

    for code in sticker_codes:
        response = (
            client.table("inventory")
            .delete()
            .eq("edition", edition)
            .eq("owner", owner)
            .eq("sticker_code", code)
            .execute()
        )

        if response.data:
            deleted += 1

    return deleted
