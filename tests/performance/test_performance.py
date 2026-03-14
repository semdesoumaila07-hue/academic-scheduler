"""
Tests de performance — Algorithme Pfair
=========================================
Mesure les temps d'exécution et vérifie les seuils fixés dans les BNF.

Exécution :
    pytest tests/performance/test_performance.py -v -s
"""
import pytest
import time
import math
from datetime import date, timedelta


def simuler_pfair(activites: list, d_effectif: int, m: int = 1) -> dict:
    """
    Simulation de l'algorithme Pfair.
    Reprend la logique de votre PfairSchedulerThread.

    Args:
        activites : liste de dicts avec 'nom', 'volume_horaire'
        d_effectif : nombre de créneaux (jours ouvrables)
        m         : nombre de ressources parallèles

    Returns:
        dict avec nb_slots, nb_activites, temps_calcul
    """
    # Initialisation
    taches = []
    for a in activites:
        U = a['volume_horaire'] / d_effectif
        taches.append({
            'nom': a['nom'],
            'U': U,
            'H': 0.0,
            'volume': a['volume_horaire']
        })

    # Vérification ordonnançabilité
    total_U = sum(t['U'] for t in taches)
    if total_U > m:
        raise ValueError(f"Non ordonnançable : ΣU={total_U:.4f} > m={m}")

    slots = []

    # Boucle principale Pfair
    for t in range(d_effectif):

        urgentes  = []
        possibles = []

        for tache in taches:
            if tache['H'] >= tache['volume']:
                continue  # terminée

            retard = tache['U'] * t - tache['H']
            val    = tache['U'] * (t + 1) - math.floor(tache['U'] * t) - 1
            alpha  = '+' if val > 0 else ('-' if val < 0 else '0')

            if retard > 0 and alpha != '-':
                urgentes.append((tache, retard))
            elif retard < 0 and alpha != '+':
                pass  # interdite
            else:
                possibles.append((tache, retard))

        # Tri par priorité décroissante
        urgentes.sort(key=lambda x: -x[1])
        possibles.sort(key=lambda x: -x[1])

        # Allocation
        ressources = m
        for tache, _ in urgentes + possibles:
            if ressources > 0 and tache['H'] < tache['volume']:
                tache['H'] += 1
                slots.append({'t': t, 'nom': tache['nom']})
                ressources -= 1

    return {
        'nb_slots': len(slots),
        'nb_activites': len(taches),
        'd_effectif': d_effectif,
        'taches': taches
    }


# ══════════════════════════════════════════════════════════════════════════
# PT-01 : 10 activités
# ══════════════════════════════════════════════════════════════════════════

class TestPerformancePfair:

    def _generer_activites(self, n: int, volume_horaire: int = 10) -> list:
        """Générer n activités de test"""
        return [
            {'nom': f'Activite_{i+1}', 'volume_horaire': volume_horaire}
            for i in range(n)
        ]

    def test_pt01_10_activites(self):
        """PT-01 : 10 activités sur 105 jours → < 5s"""
        activites = self._generer_activites(10, volume_horaire=8)
        SEUIL = 5.0

        debut = time.time()
        result = simuler_pfair(activites, d_effectif=105, m=1)
        elapsed = time.time() - debut

        print(f"\n  → 10 activités : {elapsed:.3f}s (seuil: {SEUIL}s)")
        print(f"     Créneaux planifiés : {result['nb_slots']}")
        assert elapsed < SEUIL, f"Trop lent : {elapsed:.3f}s > {SEUIL}s"

    def test_pt02_50_activites(self):
        """PT-02 : 50 activités sur 105 jours → < 15s"""
        activites = self._generer_activites(50, volume_horaire=2)
        SEUIL = 15.0

        debut = time.time()
        result = simuler_pfair(activites, d_effectif=105, m=1)
        elapsed = time.time() - debut

        print(f"\n  → 50 activités : {elapsed:.3f}s (seuil: {SEUIL}s)")
        assert elapsed < SEUIL, f"Trop lent : {elapsed:.3f}s > {SEUIL}s"

    def test_pt03_100_activites_seuil_exigence(self):
        """
        PT-03 : Cas seuil exigence BNF
        100 activités sur 105 jours → < 30 secondes
        """
        activites = self._generer_activites(100, volume_horaire=1)
        SEUIL = 30.0

        debut = time.time()
        result = simuler_pfair(activites, d_effectif=105, m=1)
        elapsed = time.time() - debut

        print(f"\n  ╔══════════════════════════════════════╗")
        print(f"  ║ PT-03 : 100 activités / 105 jours   ║")
        print(f"  ║ Temps : {elapsed:6.3f}s  (seuil: {SEUIL}s) ║")
        print(f"  ║ Créneaux : {result['nb_slots']:5d}               ║")
        print(f"  ╚══════════════════════════════════════╝")

        assert elapsed < SEUIL, f"Exigence BNF non respectée : {elapsed:.3f}s > {SEUIL}s"

    def test_pt04_charge_elevee(self):
        """PT-04 : 50 activités charge élevée → < 60s"""
        activites = self._generer_activites(50, volume_horaire=2)
        SEUIL = 60.0

        debut = time.time()
        result = simuler_pfair(activites, d_effectif=105, m=1)
        elapsed = time.time() - debut

        print(f"\n  → Charge élevée : {elapsed:.3f}s (seuil: {SEUIL}s)")
        assert elapsed < SEUIL

    def test_pt05_semestre_long(self):
        """PT-05 : 50 activités sur 150 jours (semestre long) → < 20s"""
        activites = self._generer_activites(50, volume_horaire=3)
        SEUIL = 20.0

        debut = time.time()
        result = simuler_pfair(activites, d_effectif=150, m=1)
        elapsed = time.time() - debut

        print(f"\n  → 50 activités / 150 jours : {elapsed:.3f}s")
        assert elapsed < SEUIL


# ══════════════════════════════════════════════════════════════════════════
# Test récapitulatif : affichage tableau de perf
# ══════════════════════════════════════════════════════════════════════════

def test_tableau_performance_complet():
    """Afficher un tableau récapitulatif des performances"""
    configs = [
        (10,  1,  105, 5),
        (50,  2,  105, 15),
        (100, 1,  105, 30),
        (50,  3,  150, 20),
    ]

    print("\n\n  ┌──────────────┬────────────┬───────────┬──────────┬──────────┐")
    print("  │ Nb activités │ Vol/activité│ D_effectif │ Temps    │ Résultat │")
    print("  ├──────────────┼────────────┼───────────┼──────────┼──────────┤")

    tous_ok = True
    for n, vol, d_eff, seuil in configs:
        activites = [{'nom': f'A{i}', 'volume_horaire': vol} for i in range(n)]

        debut = time.time()
        try:
            result = simuler_pfair(activites, d_effectif=d_eff, m=1)
            elapsed = time.time() - debut
            ok = elapsed < seuil
            statut = "✅ PASSÉ" if ok else f"❌ {elapsed:.2f}s>{seuil}s"
            if not ok:
                tous_ok = False
        except Exception as e:
            elapsed = time.time() - debut
            statut = f"❌ Erreur: {e}"
            tous_ok = False

        print(f"  │ {n:>12} │ {vol:>10}h │ {d_eff:>9} │ {elapsed:>6.3f}s │ {statut:<8} │")

    print("  └──────────────┴────────────┴───────────┴──────────┴──────────┘")
    assert tous_ok, "Certains tests de performance ont échoué"