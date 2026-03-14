-- Migration: Corriger les valeurs de priorité dans la base de données
-- Les priorités étaient stockées comme entiers, mais doivent être des enums

-- Mettre à jour les priorités (supposant que 1=NORMALE, 6-9=HAUTE, etc.)
UPDATE academic_activities SET priority = 'NORMALE' WHERE priority = '1';
UPDATE academic_activities SET priority = 'NORMALE' WHERE priority = '6';
UPDATE academic_activities SET priority = 'NORMALE' WHERE priority = '7';
UPDATE academic_activities SET priority = 'HAUTE' WHERE priority = '8';
UPDATE academic_activities SET priority = 'URGENTE' WHERE priority = '9';

-- Supprimer les lignes avec des valeurs invalides
DELETE FROM academic_activities WHERE priority NOT IN ('BASSE', 'NORMALE', 'HAUTE', 'URGENTE');