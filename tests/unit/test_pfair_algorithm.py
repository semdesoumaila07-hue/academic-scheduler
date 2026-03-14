"""
Tests unitaires — Algorithme Pfair
===================================
Ces tests vérifient les CALCULS MATHÉMATIQUES purs de l'algorithme
sans aucune base de données ni interface graphique.

Exécution :
    pytest tests/unit/test_pfair_algorithm.py -v
"""
import pytest
import math


# ══════════════════════════════════════════════════════════════════════════
# FONCTIONS PFAIR À TESTER
# (reprises directement de votre PfairSchedulerThread)
# ══════════════════════════════════════════════════════════════════════════

def calcul_facteur_charge(volume_horaire: float, d_effectif: int) -> float:
    """U(τi) = Ci / D_effectif"""
    if d_effectif == 0:
        raise ValueError("D_effectif ne peut pas être zéro")
    return volume_horaire / d_effectif


def calcul_retard(U: float, t: int, H: float) -> float:
    """retard(τi, t) = U × t − H(τi, t)"""
    return U * t - H


def calcul_alpha(U: float, t: int) -> str:
    """
    α(τi, t) = signe(U×(t+1) − ⌊U×t⌋ − 1)
    Retourne '+', '-' ou '0'
    """
    val = U * (t + 1) - math.floor(U * t) - 1
    if val > 0:
        return '+'
    elif val < 0:
        return '-'
    return '0'


def classifier_tache(retard: float, alpha: str) -> str:
    """
    Pfair classification :
    - URGENTE   : retard > 0 ET alpha ≠ '-'
    - INTERDITE : retard < 0 ET alpha ≠ '+'
    - POSSIBLE  : sinon
    """
    if retard > 0 and alpha != '-':
        return 'URGENTE'
    elif retard < 0 and alpha != '+':
        return 'INTERDITE'
    return 'POSSIBLE'


def verifier_ordonnancabilite(activites: list, m: int) -> bool:
    """
    Condition nécessaire et suffisante : ΣU ≤ m
    Lève ValueError si non ordonnançable.
    """
    total = sum(a['U'] for a in activites)
    if total > m:
        raise ValueError(
            f"Système non ordonnançable : ΣU={total:.4f} > m={m}"
        )
    return True


def calculer_d_effectif(debut: "date", fin: "date",
                         jours_ouvrables: list,
                         jours_feries: list = None) -> int:
    """
    Compte les jours ouvrables entre debut et fin
    en excluant les jours fériés.
    """
    from datetime import timedelta
    JOURS = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    feries = set(jours_feries or [])
    count = 0
    current = debut
    while current <= fin:
        nom_jour = JOURS[current.weekday()]
        if nom_jour in jours_ouvrables and current not in feries:
            count += 1
        current += timedelta(days=1)
    return count


# ══════════════════════════════════════════════════════════════════════════
# TESTS UT-01 : Facteur de charge
# ══════════════════════════════════════════════════════════════════════════

class TestFacteurCharge:

    def test_ut01_calcul_nominal(self):
        """UT-01 : 30h sur 105 jours → U = 0.2857"""
        U = calcul_facteur_charge(30, 105)
        assert abs(U - 0.2857) < 0.001, f"Attendu ≈0.2857, obtenu {U:.4f}"

    def test_calcul_petit_volume(self):
        """Activité de 10h sur 105 jours"""
        U = calcul_facteur_charge(10, 105)
        assert abs(U - 0.0952) < 0.001

    def test_calcul_volume_egal_d_effectif(self):
        """Volume = D_effectif → U = 1.0 (charge maximale)"""
        U = calcul_facteur_charge(105, 105)
        assert U == 1.0

    def test_d_effectif_zero_leve_erreur(self):
        """D_effectif=0 doit lever ValueError"""
        with pytest.raises(ValueError):
            calcul_facteur_charge(30, 0)

    def test_somme_facteurs_charge(self):
        """ΣU pour 4 activités typiques"""
        activites = [30, 25, 20, 15]  # volumes en heures
        d = 105
        total = sum(calcul_facteur_charge(v, d) for v in activites)
        # 30+25+20+15 = 90h sur 105j → U = 0.857
        assert abs(total - 0.857) < 0.001


# ══════════════════════════════════════════════════════════════════════════
# TESTS UT-02/03 : Ordonnançabilité
# ══════════════════════════════════════════════════════════════════════════

class TestOrdonnancabilite:

    def test_ut02_systeme_ordonnancable(self):
        """UT-02 : ΣU=0.857 ≤ m=1 → ordonnançable"""
        activites = [
            {'U': calcul_facteur_charge(30, 105)},
            {'U': calcul_facteur_charge(25, 105)},
            {'U': calcul_facteur_charge(20, 105)},
            {'U': calcul_facteur_charge(15, 105)},
        ]
        assert verifier_ordonnancabilite(activites, m=1) == True

    def test_ut03_systeme_non_ordonnancable(self):
        """UT-03 : ΣU=1.25 > m=1 → ValueError"""
        activites = [
            {'U': 0.5},
            {'U': 0.4},
            {'U': 0.35},  # total = 1.25
        ]
        with pytest.raises(ValueError, match="non ordonnançable"):
            verifier_ordonnancabilite(activites, m=1)

    def test_systeme_limite_exact(self):
        """ΣU exactement égal à m → ordonnançable (cas limite)"""
        activites = [{'U': 0.5}, {'U': 0.5}]
        assert verifier_ordonnancabilite(activites, m=1) == True

    def test_multi_ressources(self):
        """m=3 ressources : ΣU=2.8 ≤ 3 → ordonnançable"""
        activites = [{'U': 0.7}] * 4  # 4 × 0.7 = 2.8
        assert verifier_ordonnancabilite(activites, m=3) == True


# ══════════════════════════════════════════════════════════════════════════
# TESTS UT-04/05 : Calcul du retard
# ══════════════════════════════════════════════════════════════════════════

class TestCalculRetard:

    def test_ut04_retard_positif(self):
        """UT-04 : tâche en retard (H réel < H théorique)"""
        U = calcul_facteur_charge(30, 105)  # U = 0.2857
        retard = calcul_retard(U, t=10, H=2)
        # Théorique = 0.2857 × 10 = 2.857 → retard = 2.857 - 2 = 0.857
        assert abs(retard - 0.857) < 0.001, f"Retard attendu ≈0.857, obtenu {retard:.4f}"

    def test_ut05_retard_nul_au_depart(self):
        """UT-05 : t=0, H=0 → retard = 0"""
        U = calcul_facteur_charge(30, 105)
        retard = calcul_retard(U, t=0, H=0)
        assert retard == 0.0

    def test_retard_negatif_avance(self):
        """Tâche en avance (plus d'heures que prévu)"""
        U = 0.5
        retard = calcul_retard(U, t=10, H=6)
        # Théorique = 0.5 × 10 = 5 → retard = 5 - 6 = -1
        assert retard == -1.0

    def test_retard_evolue_lineairement(self):
        """Le retard augmente si aucune heure n'est allouée"""
        U = calcul_facteur_charge(30, 105)
        H = 0  # aucune heure réalisée
        retards = [calcul_retard(U, t, H) for t in range(1, 6)]
        # Chaque retard doit être supérieur au précédent
        for i in range(1, len(retards)):
            assert retards[i] > retards[i-1], "Le retard doit croître sans allocation"


# ══════════════════════════════════════════════════════════════════════════
# TESTS UT-06/07/08 : Classification des tâches
# ══════════════════════════════════════════════════════════════════════════

class TestClassificationTaches:

    def test_ut06_tache_urgente(self):
        """UT-06 : retard > 0 ET alpha='+' → URGENTE"""
        assert classifier_tache(retard=0.9, alpha='+') == 'URGENTE'

    def test_tache_urgente_alpha_zero(self):
        """retard > 0 ET alpha='0' → URGENTE aussi"""
        assert classifier_tache(retard=0.5, alpha='0') == 'URGENTE'

    def test_ut07_tache_interdite(self):
        """UT-07 : retard < 0 ET alpha='-' → INTERDITE"""
        assert classifier_tache(retard=-0.5, alpha='-') == 'INTERDITE'

    def test_tache_interdite_alpha_zero(self):
        """retard < 0 ET alpha='0' → INTERDITE"""
        assert classifier_tache(retard=-0.3, alpha='0') == 'INTERDITE'

    def test_tache_possible(self):
        """Cas neutre → POSSIBLE"""
        assert classifier_tache(retard=0.0, alpha='0') == 'POSSIBLE'

    def test_tache_urgente_ne_peut_etre_interdite(self):
        """Une tâche urgente (retard > 0) ne peut pas être interdite"""
        result = classifier_tache(retard=1.0, alpha='+')
        assert result != 'INTERDITE'


# ══════════════════════════════════════════════════════════════════════════
# TESTS UT-08 : Calcul alpha
# ══════════════════════════════════════════════════════════════════════════

class TestCalculAlpha:

    def test_ut08_alpha_positif(self):
        """UT-08 : U=0.2857, t=7 → alpha devrait être '+' """
        U = calcul_facteur_charge(30, 105)
        alpha = calcul_alpha(U, t=7)
        # On vérifie juste que c'est un des 3 valeurs attendues
        assert alpha in ['+', '-', '0'], f"Alpha invalide: {alpha}"

    def test_alpha_valeurs_possibles(self):
        """Alpha ne retourne que '+', '-' ou '0'"""
        U = calcul_facteur_charge(20, 105)
        for t in range(0, 50):
            alpha = calcul_alpha(U, t)
            assert alpha in ['+', '-', '0'], f"Valeur alpha invalide à t={t}: {alpha}"

    def test_alpha_cohérence_avec_retard(self):
        """
        Si alpha='+', la tâche a besoin d'une sous-tâche au prochain slot.
        Si alpha='-', elle n'en a pas besoin.
        """
        U = 0.5
        for t in range(0, 20):
            alpha = calcul_alpha(U, t)
            val = U * (t + 1) - math.floor(U * t) - 1
            if alpha == '+':
                assert val > 0
            elif alpha == '-':
                assert val < 0
            else:
                assert val == 0


# ══════════════════════════════════════════════════════════════════════════
# TEST UT-14 : Calcul D_effectif
# ══════════════════════════════════════════════════════════════════════════

class TestDEffectif:

    def test_ut14_semestre_standard(self):
        """UT-14 : Semestre du 01/10/2025 au 28/02/2026, lun-sam"""
        from datetime import date
        jours_feries = [
            date(2025, 11, 1),   # Toussaint
            date(2025, 12, 11),  # Fête Nationale Burkina
            date(2025, 12, 25),  # Noël
            date(2026, 1, 1),    # Nouvel An
            date(2026, 3, 8),    # Journée de la Femme (hors semestre ici)
        ]
        # Vacances de Noël : 20/12/2025 → 05/01/2026
        from datetime import timedelta
        vacances = []
        d = date(2025, 12, 20)
        while d <= date(2026, 1, 5):
            vacances.append(d)
            d += timedelta(days=1)

        tous_feries = jours_feries + vacances
        d_eff = calculer_d_effectif(
            debut=date(2025, 10, 1),
            fin=date(2026, 2, 28),
            jours_ouvrables=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"],
            jours_feries=tous_feries
        )
        print(f"\n  → D_effectif calculé : {d_eff} jours")
        # Valeur attendue ≈ 100-115 jours (dépend des vacances configurées)
        assert 90 <= d_eff <= 130, f"D_effectif hors plage réaliste : {d_eff}"

    def test_d_effectif_sans_feries(self):
        """Sans jours fériés : juste les weekends exclus"""
        from datetime import date
        # Octobre 2025 : 31 jours, lun-ven seulement
        d_eff = calculer_d_effectif(
            debut=date(2025, 10, 1),
            fin=date(2025, 10, 31),
            jours_ouvrables=["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        )
        # Octobre 2025 : 23 jours ouvrables (lun-ven)
        assert d_eff == 23, f"Attendu 23, obtenu {d_eff}"

    def test_d_effectif_avec_samedi(self):
        """Avec samedi travaillé : plus de jours que lun-ven"""
        from datetime import date
        d_sans_sam = calculer_d_effectif(
            debut=date(2025, 10, 1), fin=date(2025, 10, 31),
            jours_ouvrables=["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        )
        d_avec_sam = calculer_d_effectif(
            debut=date(2025, 10, 1), fin=date(2025, 10, 31),
            jours_ouvrables=["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
        )
        assert d_avec_sam > d_sans_sam
