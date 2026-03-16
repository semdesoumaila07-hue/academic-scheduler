"""
Gestionnaire de permissions selon les rôles.
"""


class PermissionManager:
    """Gère les permissions d'accès selon le rôle de l'utilisateur."""
    
    # Définition des permissions par rôle
    PERMISSIONS = {
        'Administrateur': [
            'dashboard',
            'structure',
            'teachers',
            'activities',
            'calendar',
            'leaves',
            'scheduling',
            'analysis',
            'reports',
            'timetable',
            'users',        # ← AJOUTÉ : Admin peut gérer les utilisateurs
        ],
        'Responsable Pédagogique': [
            'dashboard',
            'structure',
            'teachers',
            'activities',
            'calendar',
            'leaves',
            'scheduling',
            'analysis',
            'reports',
            'timetable',
        ],
        'Enseignant': [
            'dashboard',
            'activities',
            'calendar',
            'leaves',
            'timetable',
        ],
        'Étudiant': [
            'dashboard',
            'timetable',
        ],
    }
    
    @classmethod
    def get_accessible_tabs(cls, role):
        """Retourne la liste des onglets accessibles pour un rôle."""
        return cls.PERMISSIONS.get(role, ['dashboard'])
    
    @classmethod
    def can_access(cls, role, tab_name):
        """Vérifie si un rôle peut accéder à un onglet."""
        accessible = cls.get_accessible_tabs(role)
        return tab_name in accessible
    
    @classmethod
    def get_welcome_message(cls, user):
        """Retourne un message de bienvenue personnalisé."""
        role = user.get('role', 'Utilisateur')
        prenom = user.get('prenom', '')
        nom = user.get('nom', '')
        
        messages = {
            'Administrateur': (
                f"Bienvenue {prenom} {nom} !\n"
                f"Vous avez accès à toutes les fonctionnalités,\n"
                f"y compris la gestion des utilisateurs."
            ),
            'Responsable Pédagogique': (
                f"Bienvenue {prenom} {nom} !\n"
                f"Vous pouvez gérer l'ordonnancement et les rapports."
            ),
            'Enseignant': (
                f"Bienvenue {prenom} {nom} !\n"
                f"Vous pouvez consulter vos activités et congés."
            ),
            'Étudiant': (
                f"Bienvenue {prenom} {nom} !\n"
                f"Vous pouvez consulter votre emploi du temps."
            ),
        }
        