"""
Entité AcademicActivity (Activité Académique).
Cette classe implémente les paramètres de l'algorithme Pfair.
"""
from typing import Optional
from datetime import datetime, date
from ..utils.constants import ActivityType, ActivityStatus


class AcademicActivity:
    """
    Représente une activité académique avec les paramètres Pfair.
    
    Paramètres Pfair:
        - Ci: Volume horaire total (volume_hours)
        - H(t): Heures réalisées jusqu'au temps t (hours_done)
        - ri: Date d'activation (activation_date)
        - Di: Deadline (deadline)
        - Ti: Période (period)
        - U(τi): Facteur de charge (charge_factor)
    
    Attributes:
        id: Identifiant unique
        name: Nom de l'activité
        code: Code de l'activité
        type: Type d'activité (CM, TD, TP, etc.)
        volume_hours: Ci - Volume horaire total
        hours_done: H(t) - Heures réalisées
        charge_factor: U(τi) - Facteur de charge
        activation_date: ri - Date d'activation
        deadline: Di - Date limite
        period: Ti - Période en jours
        priority: Priorité (1-10)
        status: Statut de l'activité
        cohort_id: ID de la cohorte
        teacher_id: ID de l'enseignant assigné
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        code: str,
        type: ActivityType,
        volume_hours: float,  # Ci
        cohort_id: int,
        teacher_id: Optional[int] = None,
        hours_done: float = 0.0,  # H(t)
        charge_factor: float = 0.0,  # U(τi)
        activation_date: Optional[date] = None,  # ri
        deadline: Optional[date] = None,  # Di
        period: int = 0,  # Ti (en jours)
        priority: int = 1,
        status: ActivityStatus = ActivityStatus.PENDING,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une activité académique.
        
        Args:
            name: Nom de l'activité
            code: Code de l'activité
            type: Type d'activité
            volume_hours: Volume horaire total (Ci)
            cohort_id: ID de la cohorte
            teacher_id: ID de l'enseignant
            hours_done: Heures réalisées H(t)
            charge_factor: Facteur de charge U(τi)
            activation_date: Date d'activation ri
            deadline: Date limite Di
            period: Période Ti en jours
            priority: Priorité (1-10)
            status: Statut
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.code = code
        self.type = type
        self.volume_hours = volume_hours  # Ci
        self.hours_done = hours_done  # H(t)
        self.charge_factor = charge_factor  # U(τi)
        self.activation_date = activation_date  # ri
        self.deadline = deadline  # Di
        self.period = period  # Ti
        self.priority = priority
        self.status = status
        self.cohort_id = cohort_id
        self.teacher_id = teacher_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def calculate_charge_factor(self, d_effective: int) -> float:
        """
        Calcule le facteur de charge U(τi) = Ci / d_effective.
        
        Args:
            d_effective: Nombre de jours ouvrables effectifs
            
        Returns:
            Facteur de charge U(τi)
        """
        if d_effective <= 0:
            return 0.0
        
        self.charge_factor = self.volume_hours / d_effective
        return self.charge_factor
    
    def calculate_delay(self, t: int, U: float) -> float:
        """
        Calcule le retard lag(τi, t) de l'activité au temps t.
        
        lag(τi, t) = U(τi) × t - H(t)
        
        Args:
            t: Temps actuel (en jours depuis activation)
            U: Facteur de charge global du système
            
        Returns:
            Retard en heures (peut être négatif si avance)
        """
        expected_hours = self.charge_factor * t
        delay = expected_hours - self.hours_done
        return delay
    
    def calculate_alpha(self, t: int, U: float) -> float:
        """
        Calcule le ratio α(τi, t) = (U(τi) × t - H(t)) / U(τi).
        
        Ce ratio détermine si l'activité doit être ordonnancée.
        
        Args:
            t: Temps actuel
            U: Facteur de charge global
            
        Returns:
            Ratio α (entre 0 et 1 en général)
        """
        if self.charge_factor == 0:
            return 0.0
        
        delay = self.calculate_delay(t, U)
        alpha = delay / self.charge_factor
        return alpha
    
    def is_urgent(self, t: int, U: float) -> bool:
        """
        Détermine si l'activité est urgente (α >= 1).
        
        Args:
            t: Temps actuel
            U: Facteur de charge global
            
        Returns:
            True si urgente, False sinon
        """
        alpha = self.calculate_alpha(t, U)
        return alpha >= 1.0
    
    def can_execute_at(self, t: int) -> bool:
        """
        Vérifie si l'activité peut être exécutée au temps t.
        
        Args:
            t: Temps actuel
            
        Returns:
            True si exécutable, False sinon
        """
        # Vérifier si activée
        if self.activation_date:
            today = date.today()
            days_since_start = (today - self.activation_date).days
            if days_since_start < 0:
                return False
        
        # Vérifier si deadline dépassée
        if self.deadline:
            today = date.today()
            if today > self.deadline:
                return False
        
        # Vérifier si terminée
        if self.hours_done >= self.volume_hours:
            return False
        
        # Vérifier le statut
        if self.status == ActivityStatus.CANCELLED:
            return False
        
        return True
    
    def update_hours(self, hours: float) -> None:
        """
        Met à jour les heures réalisées.
        
        Args:
            hours: Heures à ajouter
        """
        self.hours_done += hours
        
        # Mettre à jour le statut
        if self.hours_done >= self.volume_hours:
            self.status = ActivityStatus.COMPLETED
        elif self.hours_done > 0:
            self.status = ActivityStatus.IN_PROGRESS
    
    def is_possible(self, t: int, U: float) -> bool:
        """
        Vérifie si l'activité est "possible" selon Pfair.
        Une activité est possible si α(τi, t) >= 0.
        
        Args:
            t: Temps actuel
            U: Facteur de charge global
            
        Returns:
            True si possible, False sinon
        """
        alpha = self.calculate_alpha(t, U)
        return alpha >= 0.0
    
    def get_remaining_hours(self) -> float:
        """
        Retourne le nombre d'heures restantes.
        
        Returns:
            Heures restantes
        """
        return max(0, self.volume_hours - self.hours_done)
    
    def get_completion_percentage(self) -> float:
        """
        Retourne le pourcentage de complétion.
        
        Returns:
            Pourcentage (0-100)
        """
        if self.volume_hours == 0:
            return 100.0
        return (self.hours_done / self.volume_hours) * 100
    
    def to_dict(self) -> dict:
        """
        Convertit l'activité en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'activité
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type.value if isinstance(self.type, ActivityType) else self.type,
            'volume_hours': self.volume_hours,
            'hours_done': self.hours_done,
            'charge_factor': self.charge_factor,
            'activation_date': self.activation_date.isoformat() if self.activation_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'period': self.period,
            'priority': self.priority,
            'status': self.status.value if isinstance(self.status, ActivityStatus) else self.status,
            'cohort_id': self.cohort_id,
            'teacher_id': self.teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AcademicActivity':
        """
        Crée une activité depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de AcademicActivity
        """
        # Convertir les enums
        activity_type = data['type']
        if isinstance(activity_type, str):
            activity_type = ActivityType(activity_type)
        
        status = data.get('status', 'En attente')
        if isinstance(status, str):
            status = ActivityStatus(status)
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            code=data['code'],
            type=activity_type,
            volume_hours=data['volume_hours'],
            cohort_id=data['cohort_id'],
            teacher_id=data.get('teacher_id'),
            hours_done=data.get('hours_done', 0.0),
            charge_factor=data.get('charge_factor', 0.0),
            activation_date=date.fromisoformat(data['activation_date']) if data.get('activation_date') else None,
            deadline=date.fromisoformat(data['deadline']) if data.get('deadline') else None,
            period=data.get('period', 0),
            priority=data.get('priority', 1),
            status=status,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'activité."""
        completion = self.get_completion_percentage()
        return f"{self.name} ({self.type.value}) - {completion:.1f}% complété"
    
    def __repr__(self) -> str:
        """Représentation technique de l'activité."""
        return f"AcademicActivity(id={self.id}, name='{self.name}', Ci={self.volume_hours}, H={self.hours_done})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de l'activité.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de l'activité est requis"
        
        if not self.code or len(self.code.strip()) == 0:
            return False, "Le code de l'activité est requis"
        
        if not isinstance(self.type, ActivityType):
            return False, "Le type doit être un ActivityType valide"
        
        if self.volume_hours <= 0:
            return False, "Le volume horaire doit être supérieur à 0"
        
        if self.hours_done < 0:
            return False, "Les heures réalisées ne peuvent pas être négatives"
        
        if self.hours_done > self.volume_hours:
            return False, "Les heures réalisées ne peuvent pas dépasser le volume horaire"
        
        if self.priority < 1 or self.priority > 10:
            return False, "La priorité doit être entre 1 et 10"
        
        if not self.cohort_id or self.cohort_id <= 0:
            return False, "L'ID de la cohorte est requis"
        
        if self.deadline and self.activation_date:
            if self.deadline < self.activation_date:
                return False, "La deadline doit être après la date d'activation"
        
        return True, None