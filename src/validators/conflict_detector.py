"""
Détecteur de conflits pour les emplois du temps.

Identifie tous les types de conflits possibles.
"""
from typing import List, Dict, Tuple
from datetime import date, time, datetime
from collections import defaultdict

from ..database.models import ScheduleSlotModel, TeacherModel, CohortModel


class ConflictDetector:
    """
    Détecteur de conflits pour les emplois du temps.
    
    Détecte :
    - Conflits d'enseignants
    - Conflits de cohortes
    - Conflits de salles
    - Chevauchements temporels
    """
    
    @staticmethod
    def detect_teacher_conflicts(slots: List[ScheduleSlotModel]) -> List[Dict]:
        """
        Détecte les conflits d'enseignants.
        
        Un conflit existe si un enseignant a 2 créneaux qui se chevauchent.
        
        Args:
            slots: Liste des créneaux à vérifier
            
        Returns:
            Liste des conflits détectés
        """
        conflicts = []
        
        # Grouper par enseignant et par date
        teacher_slots = defaultdict(lambda: defaultdict(list))
        
        for slot in slots:
            teacher_slots[slot.teacher_id][slot.date].append(slot)
        
        # Vérifier les chevauchements pour chaque enseignant
        for teacher_id, dates in teacher_slots.items():
            for slot_date, day_slots in dates.items():
                # Comparer tous les créneaux de la journée
                for i, slot1 in enumerate(day_slots):
                    for slot2 in day_slots[i+1:]:
                        if ConflictDetector._times_overlap(
                            slot1.start_time, slot1.end_time,
                            slot2.start_time, slot2.end_time
                        ):
                            conflicts.append({
                                'type': 'TEACHER_CONFLICT',
                                'teacher_id': teacher_id,
                                'date': slot_date,
                                'slot1': {
                                    'id': slot1.id,
                                    'time': f"{slot1.start_time}-{slot1.end_time}",
                                    'activity_id': slot1.activity_id,
                                    'cohort_id': slot1.cohort_id,
                                    'room': slot1.room
                                },
                                'slot2': {
                                    'id': slot2.id,
                                    'time': f"{slot2.start_time}-{slot2.end_time}",
                                    'activity_id': slot2.activity_id,
                                    'cohort_id': slot2.cohort_id,
                                    'room': slot2.room
                                },
                                'message': f"L'enseignant a 2 créneaux qui se chevauchent le {slot_date}"
                            })
        
        return conflicts
    
    @staticmethod
    def detect_cohort_conflicts(slots: List[ScheduleSlotModel]) -> List[Dict]:
        """
        Détecte les conflits de cohortes.
        
        Un conflit existe si une cohorte a 2 créneaux qui se chevauchent.
        
        Args:
            slots: Liste des créneaux à vérifier
            
        Returns:
            Liste des conflits détectés
        """
        conflicts = []
        
        # Grouper par cohorte et par date
        cohort_slots = defaultdict(lambda: defaultdict(list))
        
        for slot in slots:
            cohort_slots[slot.cohort_id][slot.date].append(slot)
        
        # Vérifier les chevauchements pour chaque cohorte
        for cohort_id, dates in cohort_slots.items():
            for slot_date, day_slots in dates.items():
                for i, slot1 in enumerate(day_slots):
                    for slot2 in day_slots[i+1:]:
                        if ConflictDetector._times_overlap(
                            slot1.start_time, slot1.end_time,
                            slot2.start_time, slot2.end_time
                        ):
                            conflicts.append({
                                'type': 'COHORT_CONFLICT',
                                'cohort_id': cohort_id,
                                'date': slot_date,
                                'slot1': {
                                    'id': slot1.id,
                                    'time': f"{slot1.start_time}-{slot1.end_time}",
                                    'activity_id': slot1.activity_id,
                                    'teacher_id': slot1.teacher_id,
                                    'room': slot1.room
                                },
                                'slot2': {
                                    'id': slot2.id,
                                    'time': f"{slot2.start_time}-{slot2.end_time}",
                                    'activity_id': slot2.activity_id,
                                    'teacher_id': slot2.teacher_id,
                                    'room': slot2.room
                                },
                                'message': f"La cohorte a 2 cours qui se chevauchent le {slot_date}"
                            })
        
        return conflicts
    
    @staticmethod
    def detect_room_conflicts(slots: List[ScheduleSlotModel]) -> List[Dict]:
        """
        Détecte les conflits de salles.
        
        Un conflit existe si une salle est utilisée par 2 créneaux qui se chevauchent.
        
        Args:
            slots: Liste des créneaux à vérifier
            
        Returns:
            Liste des conflits détectés
        """
        conflicts = []
        
        # Grouper par salle et par date
        room_slots = defaultdict(lambda: defaultdict(list))
        
        for slot in slots:
            if slot.room:  # Ignorer les créneaux sans salle
                room_slots[slot.room][slot.date].append(slot)
        
        # Vérifier les chevauchements pour chaque salle
        for room, dates in room_slots.items():
            for slot_date, day_slots in dates.items():
                for i, slot1 in enumerate(day_slots):
                    for slot2 in day_slots[i+1:]:
                        if ConflictDetector._times_overlap(
                            slot1.start_time, slot1.end_time,
                            slot2.start_time, slot2.end_time
                        ):
                            conflicts.append({
                                'type': 'ROOM_CONFLICT',
                                'room': room,
                                'date': slot_date,
                                'slot1': {
                                    'id': slot1.id,
                                    'time': f"{slot1.start_time}-{slot1.end_time}",
                                    'activity_id': slot1.activity_id,
                                    'teacher_id': slot1.teacher_id,
                                    'cohort_id': slot1.cohort_id
                                },
                                'slot2': {
                                    'id': slot2.id,
                                    'time': f"{slot2.start_time}-{slot2.end_time}",
                                    'activity_id': slot2.activity_id,
                                    'teacher_id': slot2.teacher_id,
                                    'cohort_id': slot2.cohort_id
                                },
                                'message': f"La salle {room} est utilisée par 2 cours qui se chevauchent le {slot_date}"
                            })
        
        return conflicts
    
    @staticmethod
    def detect_all_conflicts(slots: List[ScheduleSlotModel]) -> Dict[str, List[Dict]]:
        """
        Détecte tous les types de conflits.
        
        Args:
            slots: Liste des créneaux à vérifier
            
        Returns:
            Dictionnaire avec tous les conflits par type
        """
        teacher_conflicts = ConflictDetector.detect_teacher_conflicts(slots)
        cohort_conflicts = ConflictDetector.detect_cohort_conflicts(slots)
        room_conflicts = ConflictDetector.detect_room_conflicts(slots)
        
        return {
            'teacher_conflicts': teacher_conflicts,
            'cohort_conflicts': cohort_conflicts,
            'room_conflicts': room_conflicts,
            'total_conflicts': len(teacher_conflicts) + len(cohort_conflicts) + len(room_conflicts),
            'has_conflicts': (len(teacher_conflicts) + len(cohort_conflicts) + len(room_conflicts)) > 0
        }
    
    @staticmethod
    def check_single_slot_conflicts(new_slot: ScheduleSlotModel,
                                    existing_slots: List[ScheduleSlotModel]) -> Dict[str, List[Dict]]:
        """
        Vérifie si un nouveau créneau crée des conflits avec les créneaux existants.
        
        Args:
            new_slot: Nouveau créneau à vérifier
            existing_slots: Créneaux existants
            
        Returns:
            Dictionnaire avec les conflits détectés
        """
        conflicts = {
            'teacher_conflicts': [],
            'cohort_conflicts': [],
            'room_conflicts': [],
        }
        
        for slot in existing_slots:
            # Même date
            if slot.date != new_slot.date:
                continue
            
            # Vérifier chevauchement temporel
            if not ConflictDetector._times_overlap(
                new_slot.start_time, new_slot.end_time,
                slot.start_time, slot.end_time
            ):
                continue
            
            # Conflit enseignant
            if slot.teacher_id == new_slot.teacher_id:
                conflicts['teacher_conflicts'].append({
                    'type': 'TEACHER_CONFLICT',
                    'existing_slot_id': slot.id,
                    'time': f"{slot.start_time}-{slot.end_time}",
                    'message': "L'enseignant a déjà un cours à ce moment"
                })
            
            # Conflit cohorte
            if slot.cohort_id == new_slot.cohort_id:
                conflicts['cohort_conflicts'].append({
                    'type': 'COHORT_CONFLICT',
                    'existing_slot_id': slot.id,
                    'time': f"{slot.start_time}-{slot.end_time}",
                    'message': "La cohorte a déjà un cours à ce moment"
                })
            
            # Conflit salle
            if slot.room and new_slot.room and slot.room == new_slot.room:
                conflicts['room_conflicts'].append({
                    'type': 'ROOM_CONFLICT',
                    'existing_slot_id': slot.id,
                    'time': f"{slot.start_time}-{slot.end_time}",
                    'message': f"La salle {slot.room} est déjà occupée à ce moment"
                })
        
        conflicts['has_conflicts'] = (
            len(conflicts['teacher_conflicts']) > 0 or
            len(conflicts['cohort_conflicts']) > 0 or
            len(conflicts['room_conflicts']) > 0
        )
        
        return conflicts
    
    @staticmethod
    def _times_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
        """
        Vérifie si deux plages horaires se chevauchent.
        
        Args:
            start1: Heure de début 1
            end1: Heure de fin 1
            start2: Heure de début 2
            end2: Heure de fin 2
            
        Returns:
            True si chevauchement, False sinon
        """
        return start1 < end2 and end1 > start2
    
    @staticmethod
    def get_conflict_summary(conflicts: Dict[str, List[Dict]]) -> str:
        """
        Génère un résumé textuel des conflits.
        
        Args:
            conflicts: Dictionnaire des conflits
            
        Returns:
            Résumé textuel
        """
        if not conflicts.get('has_conflicts', False):
            return "✅ Aucun conflit détecté"
        
        summary = []
        
        teacher_count = len(conflicts.get('teacher_conflicts', []))
        if teacher_count > 0:
            summary.append(f"⚠️ {teacher_count} conflit(s) d'enseignant")
        
        cohort_count = len(conflicts.get('cohort_conflicts', []))
        if cohort_count > 0:
            summary.append(f"⚠️ {cohort_count} conflit(s) de cohorte")
        
        room_count = len(conflicts.get('room_conflicts', []))
        if room_count > 0:
            summary.append(f"⚠️ {room_count} conflit(s) de salle")
        
        total = teacher_count + cohort_count + room_count
        summary.insert(0, f"❌ {total} conflit(s) détecté(s)")
        
        return "\n".join(summary)
    
    @staticmethod
    def find_gaps_in_schedule(slots: List[ScheduleSlotModel], 
                             target_date: date) -> List[Dict]:
        """
        Trouve les créneaux disponibles dans une journée.
        
        Args:
            slots: Créneaux existants
            target_date: Date à analyser
            
        Returns:
            Liste des créneaux disponibles
        """
        # Filtrer les créneaux de la date
        day_slots = [s for s in slots if s.date == target_date]
        
        if not day_slots:
            return [{
                'start_time': time(8, 0),
                'end_time': time(18, 0),
                'duration_hours': 10.0
            }]
        
        # Trier par heure de début
        day_slots.sort(key=lambda s: s.start_time)
        
        gaps = []
        work_start = time(8, 0)
        work_end = time(18, 0)
        
        # Créneau avant le premier cours
        if day_slots[0].start_time > work_start:
            gaps.append({
                'start_time': work_start,
                'end_time': day_slots[0].start_time,
                'duration_hours': ConflictDetector._calculate_duration(
                    work_start, day_slots[0].start_time
                )
            })
        
        # Créneaux entre les cours
        for i in range(len(day_slots) - 1):
            gap_start = day_slots[i].end_time
            gap_end = day_slots[i+1].start_time
            
            if gap_start < gap_end:
                gaps.append({
                    'start_time': gap_start,
                    'end_time': gap_end,
                    'duration_hours': ConflictDetector._calculate_duration(gap_start, gap_end)
                })
        
        # Créneau après le dernier cours
        if day_slots[-1].end_time < work_end:
            gaps.append({
                'start_time': day_slots[-1].end_time,
                'end_time': work_end,
                'duration_hours': ConflictDetector._calculate_duration(
                    day_slots[-1].end_time, work_end
                )
            })
        
        return gaps
    
    @staticmethod
    def _calculate_duration(start_time: time, end_time: time) -> float:
        """Calcule la durée en heures entre deux horaires."""
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        return (end_dt - start_dt).total_seconds() / 3600