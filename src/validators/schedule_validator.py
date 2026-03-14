"""
Validateur pour les emplois du temps.

Vérifie la cohérence et la validité des créneaux horaires.
"""
from typing import List, Tuple, Optional
from datetime import date, time, datetime, timedelta

from ..database.models import ScheduleSlotModel, AcademicActivityModel, TeacherModel, CohortModel


class ScheduleValidator:
    """
    Validateur pour les emplois du temps.
    
    Vérifie :
    - Cohérence des horaires
    - Disponibilité des ressources
    - Respect des contraintes métier
    """
    
    @staticmethod
    def validate_time_slot(start_time: time, end_time: time) -> Tuple[bool, Optional[str]]:
        """
        Valide un créneau horaire.
        
        Args:
            start_time: Heure de début
            end_time: Heure de fin
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier que l'heure de fin est après l'heure de début
        if end_time <= start_time:
            return False, "L'heure de fin doit être après l'heure de début"
        
        # Calculer la durée
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        duration = (end_dt - start_dt).total_seconds() / 3600
        
        # Vérifier la durée minimale (30 minutes)
        if duration < 0.5:
            return False, "La durée minimale d'un créneau est de 30 minutes"
        
        # Vérifier la durée maximale (4 heures)
        if duration > 4:
            return False, "La durée maximale d'un créneau est de 4 heures"
        
        # Vérifier que les heures sont dans les plages de travail (7h-20h)
        if start_time.hour < 7 or end_time.hour > 20:
            return False, "Les créneaux doivent être entre 7h et 20h"
        
        return True, None
    
    @staticmethod
    def validate_date(slot_date: date, cohort: CohortModel) -> Tuple[bool, Optional[str]]:
        """
        Valide une date pour une cohorte.
        
        Args:
            slot_date: Date du créneau
            cohort: Cohorte concernée
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier que la date est dans la période de la cohorte
        if slot_date < cohort.start_date:
            return False, f"La date est avant le début de la cohorte ({cohort.start_date})"
        
        if slot_date > cohort.end_date:
            return False, f"La date est après la fin de la cohorte ({cohort.end_date})"
        
        # Vérifier que ce n'est pas un weekend
        if slot_date.weekday() >= 5:  # Samedi ou dimanche
            return False, "Les créneaux ne peuvent pas être planifiés le weekend"
        
        # Vérifier que ce n'est pas dans le futur lointain (> 1 an)
        one_year_later = date.today() + timedelta(days=365)
        if slot_date > one_year_later:
            return False, "Impossible de planifier plus d'un an à l'avance"
        
        return True, None
    
    @staticmethod
    def validate_teacher_workload(teacher: TeacherModel, slot_date: date, 
                                  duration_hours: float, 
                                  existing_slots: List[ScheduleSlotModel]) -> Tuple[bool, Optional[str]]:
        """
        Valide la charge de travail d'un enseignant.
        
        Args:
            teacher: Enseignant
            slot_date: Date du créneau
            duration_hours: Durée en heures
            existing_slots: Créneaux existants de l'enseignant ce jour
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Calculer les heures déjà planifiées ce jour
        total_hours = 0.0
        for slot in existing_slots:
            if slot.date == slot_date:
                start_dt = datetime.combine(date.today(), slot.start_time)
                end_dt = datetime.combine(date.today(), slot.end_time)
                total_hours += (end_dt - start_dt).total_seconds() / 3600
        
        # Vérifier la limite journalière
        if total_hours + duration_hours > teacher.max_hours_per_day:
            return False, f"L'enseignant dépasserait sa limite journalière ({teacher.max_hours_per_day}h)"
        
        # TODO: Vérifier la limite hebdomadaire
        
        return True, None
    
    @staticmethod
    def validate_activity_progress(activity: AcademicActivityModel, 
                                   hours_to_add: float) -> Tuple[bool, Optional[str]]:
        """
        Valide l'ajout d'heures à une activité.
        
        Args:
            activity: Activité académique
            hours_to_add: Heures à ajouter
            
        Returns:
            Tuple (valide, message_erreur)
        """
        if hours_to_add <= 0:
            return False, "Le nombre d'heures doit être positif"
        
        # Vérifier que ça ne dépasse pas le volume total
        new_total = activity.hours_done + hours_to_add
        if new_total > activity.volume_hours:
            remaining = activity.volume_hours - activity.hours_done
            return False, f"Dépassement du volume horaire (reste {remaining:.1f}h)"
        
        return True, None
    
    @staticmethod
    def validate_room(room: str) -> Tuple[bool, Optional[str]]:
        """
        Valide un nom de salle.
        
        Args:
            room: Nom de la salle
            
        Returns:
            Tuple (valide, message_erreur)
        """
        if not room or not room.strip():
            return False, "Le nom de la salle ne peut pas être vide"
        
        # Vérifier la longueur
        if len(room) > 50:
            return False, "Le nom de la salle est trop long (max 50 caractères)"
        
        # Vérifier le format (lettres, chiffres, tirets)
        import re
        if not re.match(r'^[A-Za-z0-9\-\s]+$', room):
            return False, "Le nom de la salle contient des caractères invalides"
        
        return True, None
    
    @staticmethod
    def validate_schedule_coherence(slots: List[ScheduleSlotModel]) -> Tuple[bool, List[str]]:
        """
        Valide la cohérence d'un ensemble de créneaux.
        
        Args:
            slots: Liste des créneaux à valider
            
        Returns:
            Tuple (valide, liste_erreurs)
        """
        errors = []
        
        # Vérifier les chevauchements
        for i, slot1 in enumerate(slots):
            for slot2 in slots[i+1:]:
                # Même jour
                if slot1.date != slot2.date:
                    continue
                
                # Chevauchement temporel
                if (slot1.start_time < slot2.end_time and 
                    slot1.end_time > slot2.start_time):
                    
                    # Même enseignant
                    if slot1.teacher_id == slot2.teacher_id:
                        errors.append(
                            f"Conflit enseignant le {slot1.date} : "
                            f"{slot1.start_time}-{slot1.end_time} et "
                            f"{slot2.start_time}-{slot2.end_time}"
                        )
                    
                    # Même cohorte
                    if slot1.cohort_id == slot2.cohort_id:
                        errors.append(
                            f"Conflit cohorte le {slot1.date} : "
                            f"{slot1.start_time}-{slot1.end_time} et "
                            f"{slot2.start_time}-{slot2.end_time}"
                        )
                    
                    # Même salle
                    if slot1.room and slot2.room and slot1.room == slot2.room:
                        errors.append(
                            f"Conflit salle {slot1.room} le {slot1.date} : "
                            f"{slot1.start_time}-{slot1.end_time} et "
                            f"{slot2.start_time}-{slot2.end_time}"
                        )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_complete_slot(slot: ScheduleSlotModel, 
                              activity: AcademicActivityModel,
                              teacher: TeacherModel,
                              cohort: CohortModel) -> Tuple[bool, List[str]]:
        """
        Validation complète d'un créneau.
        
        Args:
            slot: Créneau à valider
            activity: Activité associée
            teacher: Enseignant
            cohort: Cohorte
            
        Returns:
            Tuple (valide, liste_erreurs)
        """
        errors = []
        
        # Valider les horaires
        valid, error = ScheduleValidator.validate_time_slot(slot.start_time, slot.end_time)
        if not valid:
            errors.append(error)
        
        # Valider la date
        valid, error = ScheduleValidator.validate_date(slot.date, cohort)
        if not valid:
            errors.append(error)
        
        # Valider la salle
        if slot.room:
            valid, error = ScheduleValidator.validate_room(slot.room)
            if not valid:
                errors.append(error)
        
        # Vérifier que l'activité appartient à la cohorte
        if activity.cohort_id != cohort.id:
            errors.append("L'activité n'appartient pas à cette cohorte")
        
        # Vérifier que l'enseignant est assigné à l'activité
        if activity.teacher_id != teacher.id:
            errors.append("L'enseignant n'est pas assigné à cette activité")
        
        return len(errors) == 0, errors