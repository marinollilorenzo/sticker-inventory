# Documento di Specifiche: Gestore Inventario Figurine

## 1. Panoramica del Progetto

L'obiettivo è sviluppare una web app mobile-first in Python per la gestione di un inventario di figurine/collezionabili condiviso tra più utenti (proprietari). L'app deve permettere il controllo rapido di "mancoliste" (liste di figurine mancanti), la gestione del database e l'aggiornamento rapido delle quantità.

L'interfaccia deve essere ottimizzata per l'uso da smartphone (es. iOS via Safari) con interazioni rapide e pulite.

## 2. Stack Tecnologico

- **Frontend/Framework:** Streamlit (in hosting su Streamlit Community Cloud).
    
- **Linguaggio:** Python 3.11+
    
- **Database:** Supabase (PostgreSQL). Il tier gratuito è perfetto per questo use case, offrendo persistenza robusta, zero costi e ottime performance per query relazionali, integrandosi facilmente in Python tramite la libreria `supabase`.
    

## 3. Scelte Architetturali e di Flusso

- **Controllo per Edizione Singola:** Per evitare collisioni critiche (es. la figurina "120" esiste sia in _Panini 2014_ che in _Panini 2015_), l'interfaccia deve prevedere un menu a tendina (`st.selectbox`) in cui l'utente seleziona l'edizione _prima_ di incollare la mancolista.
    
- **Normalizzazione Input:** La mancolista incollata (formato CSV/virgole) deve subire un pre-processing automatico e invisibile:
    
    - Rimozione degli spazi bianchi iniziali e finali (`strip()`).
        
    - Conversione forzata in maiuscolo (`upper()`).
        
    - Rimozione di eventuali duplicati nell'input.
        
- **Autenticazione Leggera:** Sistema a PIN numerico. Prima di accedere alle funzioni di modifica o di ricerca, l'utente seleziona il proprio nome da una tendina e inserisce un PIN di 4 cifre per validare la sessione in `st.session_state`.
    

## 4. Funzionalità Core (Operazioni Disponibili)

L'interfaccia dovrà essere divisa in tre sezioni principali (tramite `st.tabs` o un menu laterale):

1. **Ricerca Mancolista (Il Core):**
    
    - Selezione dell'edizione e del proprietario.
        
    - `st.text_area` per incollare i dati separati da virgola.
        
    - Output: Mostrare quali figurine cercate sono presenti nel database, indicandone la quantità disponibile.
        
    - _Azione rapida:_ Un pulsante "Segna Trovate come Vendute/Scambiate" che scala automaticamente di `-1` la quantità di quelle specifiche figurine nel database (eliminando la riga se la quantità arriva a zero).
        
2. **Inventario Completo (Lettura e Export):**
    
    - Visualizzazione tabellare dell'intero database (filtrabile per proprietario/edizione).
        
    - Pulsante nativo per il download della tabella in formato CSV per backup o condivisione esterna.
        
3. **Gestione Manuale:**
    
    - Form per inserire nuove figurine o rimuoverne specifiche senza passare dalla mancolista.
        

## 5. Struttura del Database (Supabase / PostgreSQL)

È richiesta una tabella principale `inventory`:

|**Colonna**|**Tipo**|**Descrizione**|
|---|---|---|
|`id`|UUID|Chiave primaria|
|`edition`|VARCHAR|Es. "Panini 2014-2015"|
|`sticker_code`|VARCHAR|Es. "105" o "ITA04"|
|`quantity`|INT|Numero di copie possedute|
|`owner`|VARCHAR|Proprietario (es. UtenteA, UtenteB)|

_Vincolo:_ UNIQUE(`edition`, `sticker_code`, `owner`) per gestire correttamente l'upsert (aggiornamento quantità se esiste già).

## 🛠️ Direttive per il Coding Agent

Caro Agent, ti prego di implementare il progetto descritto sopra rispettando rigorosamente le seguenti linee guida ingegneristiche:

1. **Stile Pythonic e Standard:** Il codice deve essere altamente "Pythonic", pulito e modulare. Utilizza in modo estensivo i **Type Hints** (`typing`) e fornisci **Docstrings** chiare per ogni funzione. Segui rigorosamente lo standard PEP-8.
    
2. **Ottimizzazione della Logica:** Per il controllo della mancolista rispetto al database, sfrutta la potenza e l'efficienza dei `set` in Python (es. `set.intersection()`) per ottenere complessità O(1) nei lookup, evitando cicli for innestati o query ridondanti al DB.
    
3. **Architettura Modulare:** Non scrivere un singolo file monolitico. Dividi il progetto in modo logico:
    
    - `app.py` (Entry point, logica UI Streamlit)
        
    - `database.py` (Gestione della connessione Supabase e query SQL)
        
    - `utils.py` (Funzioni di pulizia e normalizzazione delle stringhe)
        
    - `auth.py` (Gestione dello stato di login via PIN in Streamlit)
        
4. **Gestione dello Stato:** Utilizza correttamente `st.session_state` per evitare che l'app perda lo stato di autenticazione o i risultati della ricerca ad ogni re-render della pagina.
    
5. **Output Richiesto:**
    
    - Fornisci tutto il codice strutturato.
        
    - Includi il file `requirements.txt` completo.
        
    - Fornisci un template per il file `.streamlit/secrets.toml` necessario per testare la connessione a Supabase.