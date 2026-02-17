# Fichier calendrier.xml

Le fichier `calendrier.xml` permet de configurer les **calendriers académiques**, **jours fériés** et **périodes de vacances** en dehors de l’interface (édition manuelle du XML ou génération par un autre outil).

## Emplacement

- Par défaut : `config/calendrier.xml`
- Vous pouvez importer un autre fichier via l’onglet **Calendrier** → **Importer depuis calendrier.xml**.

## Structure XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<calendriers>
  <calendrier>
    <nom>Nom du calendrier</nom>
    <annee_academique>2025-2026</annee_academique>
    <date_debut>2025-10-01</date_debut>
    <date_fin>2026-06-30</date_fin>
    <heures_par_jour>8</heures_par_jour>
    <nombre_semestres>2</nombre_semestres>
    <jours_feries>
      <jour_ferie>
        <nom>Nouvel An</nom>
        <date>2026-01-01</date>
        <recurrent>true</recurrent>
        <description>Optionnel</description>
      </jour_ferie>
    </jours_feries>
    <periodes_vacances>
      <periode>
        <nom>Vacances de Noël</nom>
        <date_debut>2025-12-20</date_debut>
        <date_fin>2026-01-05</date_fin>
        <type>NOEL</type>
        <description>Optionnel</description>
      </periode>
    </periodes_vacances>
  </calendrier>
</calendriers>
```

## Éléments

| Élément | Obligatoire | Description |
|--------|-------------|-------------|
| `nom` | Oui | Libellé du calendrier |
| `annee_academique` | Oui | Ex. 2025-2026 |
| `date_debut` / `date_fin` | Oui | Format ISO (YYYY-MM-DD) |
| `heures_par_jour` | Non | Défaut : 8 |
| `nombre_semestres` | Non | Défaut : 2 |
| `jours_feries` | Non | Liste de `jour_ferie` |
| `jour_ferie/nom` | Recommandé | Libellé du jour férié |
| `jour_ferie/date` | Oui | Format ISO (YYYY-MM-DD) |
| `jour_ferie/recurrent` | Non | true = même jour/mois chaque année |
| `periodes_vacances` | Non | Liste de `periode` |
| `periode/type` | Non | NOEL, PAQUES, ETE, TOUSSAINT |

## Import / Export dans l’application

- **Importer** : Onglet Calendrier → **Importer depuis calendrier.xml** (remplace les jours fériés et vacances du calendrier concerné par ceux du fichier).
- **Exporter** : Onglet Calendrier → **Exporter vers calendrier.xml** (enregistre les calendriers de la base dans un fichier XML).

Un exemple complet est fourni dans `config/calendrier.xml`.
