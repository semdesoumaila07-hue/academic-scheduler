"""
Configuration des permissions par onglet de la fenêtre principale.

Chaque onglet est associé à une permission. Seuls les utilisateurs ayant
la permission correspondante voient l'onglet.
Si current_user est None (connexion sans login), tous les onglets sont visibles.
"""
from typing import List, Tuple, Optional, Set

# (index logique, clé permission, icône, libellé menu)
# Permissions mises à jour selon les spécifications recommandées
TAB_ITEMS: List[Tuple[int, str, str, str]] = [
    (0, 'view_dashboard', '📊', 'Dashboard'),
    (1, 'manage_structure', '🏛️', 'Structure'),
    (2, 'manage_teachers', '👨‍🏫', 'Enseignants'),
    (3, 'manage_activities', '📚', 'Activités'),
    (4, 'manage_calendar', '📅', 'Calendrier'),
    (5, 'submit_leave', '🏖️', 'Congés'),
    (6, 'launch_scheduling', '⏰', 'Ordonnancement'),
    (7, 'analyze_delays', '⏱️', 'Retards'),
    (8, 'generate_reports', '📈', 'Rapports'),
    (9, 'view_timetable', '🗓️', 'Emplois du temps'),
    (10, 'declare_availability', '🕒', 'Disponibilités'),
    (12, 'manage_rooms', '🏢', 'Salles'),
    (11, 'manage_users', '👥', 'Utilisateurs'),
    (13, 'launch_scheduling', '⚡', 'Sporadiques'),
]


def get_user_permission_names(user) -> Set[str]:
    """Retourne l'ensemble des noms de permissions d'un utilisateur (tous rôles confondus)."""
    if not user:
        return set()
    names = set()
    for role in getattr(user, 'roles', []):
        for perm in getattr(role, 'permissions', []):
            if getattr(perm, 'name', None):
                names.add(perm.name)
    return names


def get_allowed_tab_indices(user) -> Optional[List[int]]:
    """
    Retourne la liste des index d'onglets autorisés pour l'utilisateur.
    Si user est None, retourne None (= tout autoriser).
    """
    if user is None:
        return None
    perms = get_user_permission_names(user)
    return [idx for idx, perm_name, _, _ in TAB_ITEMS if perm_name in perms]