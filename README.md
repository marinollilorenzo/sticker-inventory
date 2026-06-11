# 📇 Inventario Figurine

Web app mobile-first per la gestione di un inventario di figurine condiviso tra più utenti.

---

## 🚀 Setup Rapido (5 minuti)

### 1. Crea il database su Supabase (gratuito)

1. Vai su [supabase.com](https://supabase.com) e crea un account gratuito.
2. Crea un **New Project** (scegli una password e la regione EU).
3. Attendi che il progetto sia pronto (~2 minuti).
4. Vai in **SQL Editor** → **New Query**.
5. Copia e incolla il contenuto del file [`setup_database.sql`](setup_database.sql) e clicca **Run**.
6. Vai in **Settings** → **API** e copia:
   - **Project URL** (es. `https://xxxxx.supabase.co`)
   - **anon public key** (la chiave che inizia con `eyJ...`)

### 2. Configura i secrets

```bash
# Copia il template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Apri `.streamlit/secrets.toml` e inserisci:
- L'URL e la chiave API del tuo progetto Supabase
- I nomi utente e PIN per l'accesso

### 3. Installa e avvia

```bash
# Crea un virtual environment (consigliato)
python3 -m venv venv
source venv/bin/activate

# Installa le dipendenze
pip install -r requirements.txt

# Avvia l'app
streamlit run app.py
```

L'app si aprirà su `http://localhost:8501` 🎉

---

## ☁️ Deploy su Streamlit Community Cloud

1. Carica il progetto su un repository GitHub.
2. Vai su [share.streamlit.io](https://share.streamlit.io).
3. Collega il repo e seleziona `app.py` come entry point.
4. In **Advanced Settings** → **Secrets**, incolla il contenuto del tuo `secrets.toml`.
5. Clicca **Deploy** — l'app sarà online in ~1 minuto.

---

## 📱 Funzionalità

| Sezione | Cosa fa |
|---|---|
| **🔍 Mancolista** | Incolla i codici cercati e scopri quali sono disponibili |
| **📋 Inventario** | Visualizza tutto l'inventario con filtri ed export CSV |
| **✏️ Gestione** | Aggiungi o rimuovi figurine manualmente |

---

## 📂 Struttura del Progetto

```
research-figurine/
├── app.py                  # Entry point Streamlit (UI)
├── database.py             # Connessione Supabase e query
├── auth.py                 # Autenticazione con PIN
├── utils.py                # Funzioni di utilità e normalizzazione
├── requirements.txt        # Dipendenze Python
├── setup_database.sql      # Schema SQL per Supabase
├── .gitignore              # File ignorati da Git
└── .streamlit/
    ├── config.toml         # Tema Streamlit (dark mode)
    └── secrets.toml.example # Template per i secrets
```
