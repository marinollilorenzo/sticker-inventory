"""
utils.py – Funzioni di utilità per la pulizia e normalizzazione dell'input.

Modulo dedicato al pre-processing delle mancoliste incollate dall'utente,
garantendo input puliti e consistenti prima di qualsiasi operazione sul DB.
"""

from __future__ import annotations


def parse_sticker_list(raw_input: str) -> list[str]:
    """Normalizza una stringa CSV di codici figurine.

    Esegue le seguenti operazioni in sequenza:
    1. Split per virgola.
    2. Strip degli spazi bianchi.
    3. Conversione in MAIUSCOLO.
    4. Rimozione dei duplicati (preservando l'ordine).
    5. Esclusione delle stringhe vuote.

    Args:
        raw_input: Testo grezzo incollato dall'utente (es. "105, 120, ita04, 105").

    Returns:
        Lista ordinata e de-duplicata di codici figurine normalizzati.

    Examples:
        >>> parse_sticker_list("105, 120, ita04, 105")
        ['105', '120', 'ITA04']
        >>> parse_sticker_list("")
        []
    """
    seen: set[str] = set()
    result: list[str] = []

    for token in raw_input.split(","):
        code = token.strip().upper()
        if code and code not in seen:
            seen.add(code)
            result.append(code)

    return result


def format_sticker_list(codes: list[str]) -> str:
    """Converte una lista di codici in una stringa leggibile separata da virgole.

    Args:
        codes: Lista di codici figurine.

    Returns:
        Stringa formattata (es. "105, 120, ITA04").
    """
    return ", ".join(codes)


def parse_sticker_list_with_counts(raw_input: str) -> dict[str, int]:
    """Normalizza una stringa CSV e conta le occorrenze dei codici.

    Utile per l'inserimento, in modo che inserendo "772,772,772" il sistema
    capisca che si vogliono inserire 3 copie della figurina 772.

    Args:
        raw_input: Testo grezzo incollato dall'utente.

    Returns:
        Dizionario {codice_figurina: occorrenze}.
    """
    counts: dict[str, int] = {}
    for token in raw_input.split(","):
        code = token.strip().upper()
        if code:
            counts[code] = counts.get(code, 0) + 1
    return counts
