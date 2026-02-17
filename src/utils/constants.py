"""
Constantes et énumérations du système.
Correspond aux enums du modèle de base de données.
"""
import enum


class ProgramLevel(enum.Enum):
    """Niveaux de programmes."""
    LICENCE_1 = "Licence 1"
    LICENCE_2 = "Licence 2"
    LICENCE_3 = "Licence 3"
    MASTER_1 = "Master 1"
    MASTER_2 = "Master 2"
    DOCTORAT = "Doctorat"


class ActivityType(enum.Enum):
    """Types d'activités académiques."""
    COURS_MAGISTRAL = "Cours Magistral"
    TD = "Travaux Dirigés"
    TP = "Travaux Pratiques"
    EXAMEN = "Examen"
    SOUTENANCE = "Soutenance"
    SEMINAIRE = "Séminaire"


class ActivityStatus(enum.Enum):
    """Statuts des activités."""
    PENDING = "En attente"
    SCHEDULED = "Planifié"
    IN_PROGRESS = "En cours"
    COMPLETED = "Terminé"
    CANCELLED = "Annulé"


class TeacherStatus(enum.Enum):
    """Statuts des enseignants."""
    PERMANENT = "Permanent"
    VACATAIRE = "Vacataire"
    INVITE = "Invité"


class LeaveStatus(enum.Enum):
    """Statuts des demandes de congés."""
    PENDING = "En attente"
    APPROVED = "Approuvé"
    REJECTED = "Rejeté"
    CANCELLED = "Annulé"


class LeaveType(enum.Enum):
    """Types de congés."""
    MALADIE = "Maladie"
    CONGE_ANNUEL = "Congé annuel"
    FORMATION = "Formation"
    MATERNITE = "Maternité/Paternité"
    SANS_SOLDE = "Sans solde"
    AUTRE = "Autre"


class VacationType(enum.Enum):
    """Types de périodes de vacances."""
    NOEL = "Vacances de Noël"
    PAQUES = "Vacances de Pâques"
    ETE = "Vacances d'été"
    TOUSSAINT = "Vacances de Toussaint"
