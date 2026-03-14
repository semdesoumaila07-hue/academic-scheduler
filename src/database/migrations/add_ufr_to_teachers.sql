-- Migration: Ajouter ufr_id à la table teachers
-- Date: 2026-02-18
-- Description: Ajout du champ ufr_id pour rattacher les enseignants à une UFR

-- Ajouter la colonne ufr_id
ALTER TABLE teachers ADD COLUMN ufr_id INTEGER;

-- Ajouter la contrainte de clé étrangère
-- Note: SQLite ne supporte pas ALTER TABLE pour ajouter des FK directement
-- Cette migration doit être appliquée manuellement ou via un script Python

-- Créer l'index
CREATE INDEX IF NOT EXISTS idx_teachers_ufr ON teachers(ufr_id);