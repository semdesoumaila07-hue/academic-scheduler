"""
Repository pour les Créneaux Horaires (Schedule Slots).
"""
from typing import List, Optional
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .base_repository import BaseRepository
from ..models import ScheduleSlotModel


class ScheduleRepository(BaseRepository[ScheduleSlotModel]):
    """Repository pour les opérations sur les créneaux horaires."""
    
    def __init__(self, session: Session):
        super().__init__(ScheduleSlotModel, session)
    
    def get_by_date(self, target_date: date) -> List[ScheduleSlotModel]:
        """Récupère tous les créneaux d'une date."""
        return self.filter_by(date=target_date)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[ScheduleSlotModel]:
        """Récupère tous les créneaux d'une période."""
        return self.session.query(self.model).filter(
            and_(
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        ).order_by(self.model.date, self.model.start_time).all()
    
    def get_by_cohort(self, cohort_id: int, start_date: date = None, end_date: date = None) -> List[ScheduleSlotModel]:
        """Récupère l'emploi du temps d'une cohorte."""
        query = self.session.query(self.model).filter(self.model.cohort_id == cohort_id)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
        
        return query.order_by(self.model.date, self.model.start_time).all()
    
    def get_by_teacher(self, teacher_id: int, start_date: date = None, end_date: date = None) -> List[ScheduleSlotModel]:
        """Récupère l'emploi du temps d'un enseignant."""
        query = self.session.query(self.model).filter(self.model.teacher_id == teacher_id)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
        
        return query.order_by(self.model.date, self.model.start_time).all()
    
    def get_by_activity(self, activity_id: int) -> List[ScheduleSlotModel]:
        """Récupère tous les créneaux d'une activité."""
        return self.filter_by(activity_id=activity_id)
    
    def get_by_room(self, room: str, start_date: date = None, end_date: date = None) -> List[ScheduleSlotModel]:
        """Récupère tous les créneaux d'une salle."""
        query = self.session.query(self.model).filter(self.model.room == room)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
        
        return query.order_by(self.model.date, self.model.start_time).all()
    
    def check_conflict(self, target_date: date, start_time: time, end_time: time,
                      teacher_id: int = None, cohort_id: int = None, room: str = None) -> bool:
        """
        Vérifie s'il y a un conflit pour un créneau.
        
        Args:
            target_date: Date du créneau
            start_time: Heure de début
            end_time: Heure de fin
            teacher_id: ID de l'enseignant (optionnel)
            cohort_id: ID de la cohorte (optionnel)
            room: Salle (optionnel)
            
        Returns:
            True s'il y a un conflit, False sinon
        """
        # Construire la requête de base pour détecter les chevauchements temporels
        query = self.session.query(self.model).filter(
            and_(
                self.model.date == target_date,
                or_(
                    and_(self.model.start_time <= start_time, self.model.end_time > start_time),
                    and_(self.model.start_time < end_time, self.model.end_time >= end_time),
                    and_(self.model.start_time >= start_time, self.model.end_time <= end_time)
                )
            )
        )
        
        # Ajouter les filtres de conflit
        conditions = []
        if teacher_id:
            conditions.append(self.model.teacher_id == teacher_id)
        if cohort_id:
            conditions.append(self.model.cohort_id == cohort_id)
        if room:
            conditions.append(self.model.room == room)
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        return query.count() > 0
    
    def get_available_rooms(self, target_date: date, start_time: time, end_time: time,
                           all_rooms: List[str]) -> List[str]:
        """
        Retourne les salles disponibles pour un créneau.
        
        Args:
            target_date: Date
            start_time: Heure de début
            end_time: Heure de fin
            all_rooms: Liste de toutes les salles
            
        Returns:
            Liste des salles disponibles
        """
        # Récupérer les salles occupées
        occupied_rooms = self.session.query(self.model.room).filter(
            and_(
                self.model.date == target_date,
                self.model.room.isnot(None),
                or_(
                    and_(self.model.start_time <= start_time, self.model.end_time > start_time),
                    and_(self.model.start_time < end_time, self.model.end_time >= end_time),
                    and_(self.model.start_time >= start_time, self.model.end_time <= end_time)
                )
            )
        ).all()
        
        occupied_rooms = [r[0] for r in occupied_rooms if r[0]]
        
        # Retourner les salles disponibles
        return [room for room in all_rooms if room not in occupied_rooms]
    
    def get_blocked_slots(self, start_date: date = None, end_date: date = None) -> List[ScheduleSlotModel]:
        """Récupère tous les créneaux bloqués (par congés)."""
        query = self.session.query(self.model).filter(self.model.blocked_by_leave == True)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
        
        return query.all()
    
    def block_slots_by_leave(self, teacher_id: int, start_date: date, end_date: date) -> int:
        """
        Bloque tous les créneaux d'un enseignant pendant une période de congé.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début du congé
            end_date: Date de fin du congé
            
        Returns:
            Nombre de créneaux bloqués
        """
        slots = self.session.query(self.model).filter(
            and_(
                self.model.teacher_id == teacher_id,
                self.model.date >= start_date,
                self.model.date <= end_date,
                self.model.blocked_by_leave == False
            )
        ).all()
        
        count = 0
        for slot in slots:
            slot.blocked_by_leave = True
            slot.notes = f"Enseignant en congé ({start_date} - {end_date})"
            count += 1
        
        if count > 0:
            self.session.commit()
        
        return count
    
    def unblock_slots_by_leave(self, teacher_id: int, start_date: date, end_date: date) -> int:
        """
        Débloque les créneaux d'un enseignant (congé annulé).
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Nombre de créneaux débloqués
        """
        slots = self.session.query(self.model).filter(
            and_(
                self.model.teacher_id == teacher_id,
                self.model.date >= start_date,
                self.model.date <= end_date,
                self.model.blocked_by_leave == True
            )
        ).all()
        
        count = 0
        for slot in slots:
            slot.blocked_by_leave = False
            slot.notes = None
            count += 1
        
        if count > 0:
            self.session.commit()
        
        return count
    
    def delete_by_cohort(self, cohort_id: int, start_date: date = None, end_date: date = None) -> int:
        """
        Supprime tous les créneaux d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Nombre de créneaux supprimés
        """
        query = self.session.query(self.model).filter(self.model.cohort_id == cohort_id)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date >= start_date,
                    self.model.date <= end_date
                )
            )
        
        count = query.count()
        query.delete()
        self.session.commit()
        
        return count