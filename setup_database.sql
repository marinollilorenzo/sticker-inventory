-- ============================================
-- Schema Database per Inventario Figurine
-- ============================================
-- Esegui questo SQL nell'editor SQL di Supabase:
-- https://supabase.com/dashboard → Progetto → SQL Editor → New Query
--
-- IMPORTANTE: Assicurati che l'estensione uuid-ossp sia abilitata
-- (di default è già attiva su Supabase).

-- Abilita l'estensione UUID se non già attiva
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabella principale dell'inventario
CREATE TABLE IF NOT EXISTS inventory (
    id          UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    edition     VARCHAR(255) NOT NULL,
    sticker_code VARCHAR(50) NOT NULL,
    quantity    INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    owner       VARCHAR(100) NOT NULL,

    -- Vincolo di unicità: una sola riga per combinazione edizione+codice+proprietario
    CONSTRAINT unique_sticker_per_owner UNIQUE (edition, sticker_code, owner)
);

-- Indici per velocizzare le query più frequenti
CREATE INDEX IF NOT EXISTS idx_inventory_edition ON inventory (edition);
CREATE INDEX IF NOT EXISTS idx_inventory_owner ON inventory (owner);
CREATE INDEX IF NOT EXISTS idx_inventory_edition_owner ON inventory (edition, owner);

-- Abilita Row Level Security (RLS) - necessario per Supabase
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;

-- Policy: permetti tutte le operazioni tramite anon key
-- (l'autenticazione è gestita a livello applicativo con PIN)
CREATE POLICY "Allow all operations" ON inventory
    FOR ALL
    USING (true)
    WITH CHECK (true);
