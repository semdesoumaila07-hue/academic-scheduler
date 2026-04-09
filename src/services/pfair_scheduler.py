"""
Implémentation de l'algorithme Pfair pour l'ordonnancement académique.

L'algorithme Pfair (Proportionate Fair) garantit un ordonnancement équitable
en maintenant la proportionnalité entre le temps écoulé et le travail effectué.

Concepts clés :
- Ci : Volume horaire total d'une activité
- H(t) : Heures réalisées jusqu'au temps t
- U(τi) : Facteur de charge = Ci / D_effectif
- lag(τi, t) : Retard = U(τi) × t - H(t)
- α(τi, t) : Ratio = lag(τi, t) / U(τi)

CORRECTIONS apportées :
- schedule_cohort        : calendar_id récupéré UNE SEULE FOIS et passé à tous
                           les appels (calculate_effective_days, is_workday).
- is_schedulable         : calendar_id désormais récupéré et transmis à
                           calculate_effective_days.
- accept_sporadic_task / schedule_sporadic_task : idem.
- NOUVEAU — congés enseignants : la boucle Pfair vérifie maintenant si
                           l'enseignant est en congé APPROUVÉ avant d'allouer
                           un créneau. Si congé actif → conflit enregistré,
                           créneau ignoré. Idem dans schedule_sporadic_task.
"""
from typing import List, Optional, Dict, Tuple
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session

from ..database.models import (
    AcademicActivityModel, ScheduleSlotModel, TeacherModel,
    CohortModel, ActivityStatusEnum, TeacherAvailabilityModel,
    LeaveRequestModel, LeaveStatusEnum
)
from ..database.repositories import (
    ActivityRepository, ScheduleRepository, TeacherRepository,
    CohortRepository, CalendarRepository
)
from .calendar_service import CalendarService


class PfairScheduler:
    """
    Ordonnanceur Pfair pour les activités académiques.

    Attributes:
        session: Session de base de données
        calendar_service: Service de gestion du calendrier
    """

    def __init__(self, session: Session):
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.calendar_repo = CalendarRepository(session)
        self.calendar_service = CalendarService(session)

    # ──────────────────────────────────────────────────────────────────────────
    # Méthodes utilitaires internes
    # ──────────────────────────────────────────────────────────────────────────

    def _get_calendar_id(self, reference_date: date) -> Optional[int]:
        """
        Résout le calendar_id actif pour une date de référence donnée.

        Utilise la date de début de la période d'ordonnancement comme ancre,
        ce qui garantit que tous les appels (calculate_effective_days,
        is_workday, is_holiday…) utilisent le MÊME calendrier.
        """
        calendar = self.calendar_repo.get_current_calendar(reference_date)
        return calendar.id if calendar else None

    def _is_teacher_on_leave(self, teacher_id: int, check_date: date) -> bool:
        """
        Vérifie si un enseignant est en congé APPROUVÉ à une date donnée.

        Consulte directement la table leave_requests pour trouver un congé
        approuvé dont la période englobe check_date.

        Args:
            teacher_id : ID de l'enseignant
            check_date : Date à vérifier

        Returns:
            True si l'enseignant est en congé approuvé ce jour-là, False sinon.
        """
        from sqlalchemy import and_

        leave = self.session.query(LeaveRequestModel).filter(
            and_(
                LeaveRequestModel.teacher_id == teacher_id,
                LeaveRequestModel.status     == LeaveStatusEnum.APPROVED,
                LeaveRequestModel.start_date <= check_date,
                LeaveRequestModel.end_date   >= check_date,
            )
        ).first()

        return leave is not None

    # ──────────────────────────────────────────────────────────────────────────
    # Ordonnancement principal
    # ──────────────────────────────────────────────────────────────────────────

    def schedule_cohort(self, cohort_id, start_date, end_date, available_rooms=None):
        """
        Génère l'emploi du temps d'une cohorte avec l'algorithme Pfair.

        Args:
            cohort_id      : ID de la cohorte
            start_date     : Date de début de la période
            end_date       : Date de fin de la période
            available_rooms: Liste des salles disponibles

        Returns:
            Dictionnaire avec les statistiques de l'ordonnancement
        """
        # ── Récupérer le calendrier UNE SEULE FOIS ───────────────────────────
        calendar_id = self._get_calendar_id(start_date)

        cohort = self.cohort_repo.get_by_id(cohort_id)
        if not cohort:
            raise ValueError(f"Cohorte {cohort_id} introuvable")

        activities = self.activity_repo.get_by_cohort(cohort_id)

        if not activities:
            return {
                'success': False,
                'message': 'Aucune activité à planifier',
                'scheduled_slots': 0
            }

        d_effective = self.calendar_service.calculate_effective_days(
            start_date, end_date, calendar_id
        )

        if d_effective <= 0:
            return {
                'success': False,
                'message': 'Aucun jour ouvrable dans la période',
                'scheduled_slots': 0
            }

        total_charge = 0.0
        for activity in activities:
            remaining_hours = activity.volume_hours - activity.hours_done
            activity.charge_factor = remaining_hours / d_effective
            total_charge += activity.charge_factor

        U = total_charge

        if U > 1.0:
            return {
                'success': False,
                'message': f'Charge totale trop élevée: {U:.2f} > 1.0',
                'total_charge': U,
                'effective_days': d_effective,
                'schedulable': False
            }

        t = 0
        current_date = start_date
        scheduled_slots = []
        conflicts = []

        # ── Boucle principale Pfair ───────────────────────────────────────────
        while current_date <= end_date:
            if not self.calendar_service.is_workday(current_date, calendar_id):
                current_date += timedelta(days=1)
                continue

            t += 1

            urgent_activities = []
            possible_activities = []

            for activity in activities:
                if activity.status in [ActivityStatusEnum.COMPLETED, ActivityStatusEnum.CANCELLED]:
                    continue

                remaining = activity.volume_hours - activity.hours_done
                if remaining <= 0:
                    activity.status = ActivityStatusEnum.COMPLETED
                    continue

                expected_hours = activity.charge_factor * t
                delay = expected_hours - activity.hours_done

                if activity.charge_factor > 0:
                    alpha = delay / activity.charge_factor
                    if alpha >= 1.0:
                        urgent_activities.append((activity, alpha, delay))
                    elif alpha >= 0:
                        possible_activities.append((activity, alpha, delay))

            urgent_activities.sort(key=lambda x: x[1], reverse=True)

            daily_slots = []
            start_hour    = 8
            slot_duration = 2

            for activity, alpha, delay in urgent_activities:

                teacher = self.teacher_repo.get_by_id(activity.teacher_id)
                if not teacher:
                    continue

                slot_start = time(hour=start_hour)
                slot_end   = time(hour=start_hour + slot_duration)

                # ── NOUVEAU : congé approuvé de l'enseignant ──────────────────
                if self._is_teacher_on_leave(teacher.id, current_date):
                    conflicts.append({
                        'date'    : current_date,
                        'activity': activity.name,
                        'reason'  : f"Enseignant {teacher.full_name} en congé approuvé"
                    })
                    continue
                # ─────────────────────────────────────────────────────────────

                # Disponibilité horaire
                day_of_week = current_date.weekday()
                has_avail = self.session.query(TeacherAvailabilityModel).filter(
                    TeacherAvailabilityModel.teacher_id == teacher.id
                ).count() > 0
                if has_avail:
                    avail_ok = self.session.query(TeacherAvailabilityModel).filter(
                        TeacherAvailabilityModel.teacher_id  == teacher.id,
                        TeacherAvailabilityModel.day_of_week == day_of_week,
                        TeacherAvailabilityModel.start_time  <= slot_start,
                        TeacherAvailabilityModel.end_time    >= slot_end,
                        TeacherAvailabilityModel.period_start <= current_date,
                        TeacherAvailabilityModel.period_end   >= current_date,
                    ).first()
                    if not avail_ok:
                        conflicts.append({
                            'date'    : current_date,
                            'activity': activity.name,
                            'reason'  : f"Enseignant {teacher.full_name} non disponible"
                        })
                        continue

                # Conflits inter-cohortes
                inter_conflict = self.session.query(ScheduleSlotModel).filter(
                    ScheduleSlotModel.teacher_id == teacher.id,
                    ScheduleSlotModel.date       == current_date,
                    ScheduleSlotModel.start_time == slot_start,
                ).first()
                if inter_conflict and inter_conflict.cohort_id != cohort_id:
                    conflicts.append({
                        'date'    : current_date,
                        'activity': activity.name,
                        'reason'  : f"Enseignant occupé par cohorte {inter_conflict.cohort_id}"
                    })
                    continue

                # Conflits intra-cohorte
                if self.schedule_repo.check_conflict(
                    current_date, slot_start, slot_end,
                    teacher_id=teacher.id, cohort_id=cohort_id
                ):
                    conflicts.append({
                        'date'    : current_date,
                        'activity': activity.name,
                        'reason'  : 'Conflit horaire'
                    })
                    continue

                # Sélection de salle
                room = None
                act_type = str(getattr(getattr(activity, 'type', None), 'value', None) or '').lower()
                type_map = {
                    'magistral': ['AMPHI', 'TD'],
                    'dirige'   : ['TD', 'AMPHI'],
                    'pratique' : ['TP', 'LABO', 'INFORMATIQUE'],
                    'td'       : ['TD', 'AMPHI'],
                    'tp'       : ['TP', 'LABO', 'INFORMATIQUE'],
                    'cm'       : ['AMPHI', 'TD'],
                }
                preferred = None
                for key, types in type_map.items():
                    if key in act_type:
                        preferred = types
                        break

                required_capacity = cohort.student_count if cohort.student_count else 0

                if available_rooms:
                    from sqlalchemy import text as sqlt
                    from src.database.models import RoomModel
                    for ptype in (preferred or ['AMPHI', 'TD', 'TP', 'LABO', 'INFORMATIQUE', 'AUTRE']):
                        names = tuple(available_rooms) if len(available_rooms) > 1 else (available_rooms[0], available_rooms[0])
                        rows = self.session.execute(sqlt(
                            'SELECT name FROM rooms'
                            ' WHERE room_type=:rt AND is_active=1'
                            '   AND name IN :names'
                            '   AND capacity >= :cap'
                            '   AND name NOT IN ('
                            '       SELECT room FROM schedule_slots'
                            '       WHERE date=:d AND start_time=:st AND room IS NOT NULL'
                            '   )'
                            ' ORDER BY capacity ASC'
                        ), {
                            'rt': ptype, 'names': names,
                            'cap': required_capacity,
                            'd': str(current_date), 'st': str(slot_start)
                        }).fetchall()
                        if rows:
                            room = rows[0][0]
                            break

                    if not room:
                        rows = self.session.execute(sqlt(
                            'SELECT name FROM rooms'
                            ' WHERE is_active=1'
                            '   AND name IN :names'
                            '   AND capacity >= :cap'
                            '   AND name NOT IN ('
                            '       SELECT room FROM schedule_slots'
                            '       WHERE date=:d AND start_time=:st AND room IS NOT NULL'
                            '   )'
                            ' ORDER BY capacity ASC'
                        ), {
                            'names': names,
                            'cap': required_capacity,
                            'd': str(current_date), 'st': str(slot_start)
                        }).fetchall()
                        if rows:
                            room = rows[0][0]

                    if not room:
                        rows = self.session.execute(sqlt(
                            'SELECT name, capacity FROM rooms'
                            ' WHERE is_active=1'
                            '   AND name IN :names'
                            '   AND name NOT IN ('
                            '       SELECT room FROM schedule_slots'
                            '       WHERE date=:d AND start_time=:st AND room IS NOT NULL'
                            '   )'
                            ' ORDER BY capacity DESC'
                        ), {
                            'names': names,
                            'd': str(current_date), 'st': str(slot_start)
                        }).fetchall()
                        if rows:
                            room = rows[0][0]
                            room_cap = rows[0][1] if len(rows[0]) > 1 else 0
                            conflicts.append({
                                'date'    : current_date,
                                'activity': activity.name,
                                'reason'  : (
                                    f"Surcharge salle : {room} ({room_cap} places)"
                                    f" < effectif cohorte ({required_capacity} étudiants)"
                                )
                            })

                if room:
                    rc = self.session.query(ScheduleSlotModel).filter(
                        ScheduleSlotModel.room       == room,
                        ScheduleSlotModel.date       == current_date,
                        ScheduleSlotModel.start_time == slot_start,
                    ).first()
                    if rc:
                        room = None

                slot = ScheduleSlotModel(
                    date        = current_date,
                    start_time  = slot_start,
                    end_time    = slot_end,
                    room        = room,
                    activity_id = activity.id,
                    teacher_id  = teacher.id,
                    cohort_id   = cohort_id,
                    delay_value = delay
                )

                daily_slots.append(slot)
                scheduled_slots.append(slot)

                activity.hours_done += slot_duration
                activity.status = ActivityStatusEnum.IN_PROGRESS

                start_hour += slot_duration
                if start_hour >= 16:
                    break

            for slot in daily_slots:
                self.session.add(slot)

            current_date += timedelta(days=1)

        self.session.commit()

        total_scheduled_hours = len(scheduled_slots) * 2
        leave_conflicts = sum(1 for c in conflicts if 'congé' in c.get('reason', '').lower())

        return {
            'success'          : True,
            'scheduled_slots'  : len(scheduled_slots),
            'total_hours'      : total_scheduled_hours,
            'conflicts'        : len(conflicts),
            'leave_conflicts'  : leave_conflicts,
            'total_charge'     : U,
            'effective_days'   : d_effective,
            'schedulable'      : True,
            'period'           : f"{start_date} à {end_date}",
            'conflicts_details': conflicts
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Priorité d'une activité
    # ──────────────────────────────────────────────────────────────────────────

    def calculate_activity_priority(self, activity: AcademicActivityModel, t: int) -> Tuple[float, float]:
        """Calcule la priorité d'ordonnancement d'une activité."""
        if activity.charge_factor == 0:
            return (0.0, 0.0)
        expected_hours = activity.charge_factor * t
        delay = expected_hours - activity.hours_done
        alpha = delay / activity.charge_factor
        return (alpha, delay)

    # ──────────────────────────────────────────────────────────────────────────
    # Salles compatibles
    # ──────────────────────────────────────────────────────────────────────────

    def get_compatible_rooms(self, cohort_id: int,
                             target_date: date, slot_start, slot_end,
                             available_rooms: List[str] = None,
                             activity_type: str = "") -> Dict:
        """Retourne les salles compatibles pour un créneau donné."""
        from src.database.models import RoomModel
        from sqlalchemy import text as sqlt

        cohort   = self.cohort_repo.get_by_id(cohort_id)
        required = cohort.student_count if cohort and cohort.student_count else 0

        occupied = {
            r[0] for r in self.session.execute(sqlt(
                'SELECT room FROM schedule_slots'
                ' WHERE date=:d AND start_time=:st AND room IS NOT NULL'
            ), {'d': str(target_date), 'st': str(slot_start)}).fetchall()
        }

        query = self.session.query(RoomModel).filter(RoomModel.is_active == True)
        if available_rooms:
            query = query.filter(RoomModel.name.in_(available_rooms))

        all_rooms = query.order_by(RoomModel.capacity.asc()).all()

        result = []
        for r in all_rooms:
            if r.name in occupied:
                continue
            fit = "ok" if r.capacity >= required else "surcharge"
            result.append({
                'name'     : r.name,
                'capacity' : r.capacity,
                'room_type': r.room_type,
                'fit'      : fit,
            })

        adequate = [r for r in result if r['fit'] == 'ok']
        best = adequate[0]['name'] if adequate else (result[0]['name'] if result else None)

        return {
            'rooms'       : result,
            'cohort_size' : required,
            'has_adequate': len(adequate) > 0,
            'best_room'   : best,
        }

    def check_room_capacity(self, room_name: str, cohort_id: int) -> Dict:
        """Vérifie si une salle est compatible avec l'effectif d'une cohorte."""
        from src.database.models import RoomModel
        room   = self.session.query(RoomModel).filter_by(name=room_name).first()
        cohort = self.cohort_repo.get_by_id(cohort_id)

        room_cap  = room.capacity if room else 0
        cohort_sz = cohort.student_count if cohort and cohort.student_count else 0
        overflow  = cohort_sz - room_cap

        return {
            'compatible'    : overflow <= 0,
            'room_capacity' : room_cap,
            'cohort_size'   : cohort_sz,
            'overflow'      : overflow,
            'room_name'     : room_name,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Test de faisabilité
    # ──────────────────────────────────────────────────────────────────────────

    def is_schedulable(self, cohort_id: int, start_date: date, end_date: date) -> Dict:
        """
        Vérifie si une cohorte peut être ordonnancée (test de faisabilité).
        calendar_id résolu depuis start_date → cohérent avec schedule_cohort.
        """
        activities = self.activity_repo.get_by_cohort(cohort_id)

        if not activities:
            return {'schedulable': False, 'reason': 'Aucune activité', 'total_charge': 0.0}

        calendar_id = self._get_calendar_id(start_date)

        d_effective = self.calendar_service.calculate_effective_days(
            start_date, end_date, calendar_id
        )

        if d_effective <= 0:
            return {
                'schedulable': False,
                'reason': 'Aucun jour ouvrable',
                'total_charge': 0.0,
                'effective_days': 0
            }

        total_charge = 0.0
        for activity in activities:
            remaining = activity.volume_hours - activity.hours_done
            if remaining > 0:
                total_charge += remaining / d_effective

        schedulable = total_charge <= 1.0

        return {
            'schedulable'   : schedulable,
            'total_charge'  : total_charge,
            'effective_days': d_effective,
            'reason'        : 'OK' if schedulable else f'Charge trop élevée: {total_charge:.2f} > 1.0',
            'max_charge'    : 1.0
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Rééquilibrage
    # ──────────────────────────────────────────────────────────────────────────

    def rebalance_schedule(self, cohort_id: int, start_date: date, end_date: date) -> Dict:
        """Réajuste l'emploi du temps pour minimiser les retards."""
        deleted_count = self.schedule_repo.delete_by_cohort(cohort_id, start_date, end_date)
        result = self.schedule_cohort(cohort_id, start_date, end_date)
        result['deleted_slots'] = deleted_count
        result['rebalanced']    = True
        return result

    # ══════════════════════════════════════════════════════════════════════════
    # GESTION DES TÂCHES SPORADIQUES
    # ══════════════════════════════════════════════════════════════════════════

    def accept_sporadic_task(self, activity_id: int,
                             start_date: date, end_date: date) -> Dict:
        """
        Test d'acceptation de Liu & Layland pour une tâche sporadique.
        ΣU_périodiques + Us ≤ 1.0  où  Us = Cs / ds
        """
        from src.database.models import AcademicActivityModel as AAM
        activity = self.session.query(AAM).get(activity_id)
        if not activity:
            return {'accepted': False, 'reason': f'Activité {activity_id} introuvable'}
        if not getattr(activity, 'is_sporadic', False):
            return {'accepted': False, 'reason': "Cette activité n'est pas marquée comme sporadique"}

        cohort_id = activity.cohort_id
        arr    = getattr(activity, 'arrival_date', None) or start_date
        window = getattr(activity, 'execution_window', None) or 0
        if window <= 0:
            return {'accepted': False, 'reason': 'execution_window doit être > 0'}

        deadline = arr + timedelta(days=window)

        calendar_id_arr = self._get_calendar_id(arr)
        d_window = self.calendar_service.calculate_effective_days(arr, deadline, calendar_id_arr)
        if d_window <= 0:
            return {'accepted': False, 'reason': "Aucun jour ouvrable dans la fenêtre d'exécution"}

        remaining  = max(0.0, activity.volume_hours - (activity.hours_done or 0))
        u_sporadic = remaining / d_window

        calendar_id = self._get_calendar_id(start_date)
        d_effective = self.calendar_service.calculate_effective_days(start_date, end_date, calendar_id)
        if d_effective <= 0:
            return {'accepted': False, 'reason': 'Période de référence invalide'}

        from src.database.models import ActivityStatusEnum as ASE
        periodic = self.session.query(AAM).filter(
            AAM.cohort_id   == cohort_id,
            AAM.id          != activity_id,
            AAM.is_sporadic == False,
            AAM.status.notin_([ASE.COMPLETED, ASE.CANCELLED])
        ).all()

        u_periodic_sum = sum(
            max(0.0, a.volume_hours - (a.hours_done or 0)) / d_effective
            for a in periodic
            if (a.volume_hours - (a.hours_done or 0)) > 0
        )

        u_total  = u_periodic_sum + u_sporadic
        residual = 1.0 - u_periodic_sum
        accepted = u_total <= 1.0

        return {
            'accepted'         : accepted,
            'reason'           : 'OK' if accepted else (
                f'Test refusé : ΣU_périodiques ({u_periodic_sum:.4f}) '
                f'+ Us ({u_sporadic:.4f}) = {u_total:.4f} > 1.0'
            ),
            'u_sporadic'       : round(u_sporadic, 4),
            'u_periodic_sum'   : round(u_periodic_sum, 4),
            'u_total'          : round(u_total, 4),
            'residual_capacity': round(residual, 4),
            'd_window'         : d_window,
            'deadline'         : deadline,
        }

    def schedule_sporadic_task(self, activity_id: int,
                               start_date: date, end_date: date,
                               available_rooms: List[str] = None) -> Dict:
        """
        Planifie une tâche sporadique via EDF après test d'acceptation.
        Les créneaux sont alloués en priorité sur 14h, 16h, 8h, 10h, 12h.
        """
        from src.database.models import AcademicActivityModel as AAM
        from src.database.models import ActivityStatusEnum as ASE

        test = self.accept_sporadic_task(activity_id, start_date, end_date)
        if not test['accepted']:
            return {
                'success'        : False,
                'reason'         : "Test d'acceptation échoué : " + test['reason'],
                'test'           : test,
                'scheduled_slots': 0,
            }

        activity  = self.session.query(AAM).get(activity_id)
        cohort_id = activity.cohort_id
        teacher   = self.teacher_repo.get_by_id(activity.teacher_id) if activity.teacher_id else None
        if not teacher:
            return {'success': False, 'reason': 'Aucun enseignant assigné à cette activité'}

        arrival  = getattr(activity, 'arrival_date', None) or start_date
        deadline = test['deadline']

        plan_start = max(start_date, arrival)
        plan_end   = min(end_date, deadline)

        remaining_hours = max(0.0, activity.volume_hours - (activity.hours_done or 0))
        slot_duration   = 2
        slots_needed    = int(remaining_hours / slot_duration) + (1 if remaining_hours % slot_duration > 0 else 0)

        calendar_id     = self._get_calendar_id(plan_start)
        scheduled_slots = []
        conflicts       = []
        current_date    = plan_start

        while current_date <= plan_end and slots_needed > 0:
            if not self.calendar_service.is_workday(current_date, calendar_id):
                current_date += timedelta(days=1)
                continue

            for start_hour in [14, 16, 8, 10, 12]:
                end_hour = start_hour + slot_duration
                if end_hour > 20:
                    continue
                slot_start_t = time(hour=start_hour)
                slot_end_t   = time(hour=end_hour)

                # ── Vérifier congé enseignant ─────────────────────────────────
                if self._is_teacher_on_leave(teacher.id, current_date):
                    continue
                # ─────────────────────────────────────────────────────────────

                day_of_week = current_date.weekday()
                has_avail = self.session.query(TeacherAvailabilityModel).filter(
                    TeacherAvailabilityModel.teacher_id == teacher.id
                ).count() > 0
                if has_avail:
                    avail_ok = self.session.query(TeacherAvailabilityModel).filter(
                        TeacherAvailabilityModel.teacher_id  == teacher.id,
                        TeacherAvailabilityModel.day_of_week == day_of_week,
                        TeacherAvailabilityModel.start_time  <= slot_start_t,
                        TeacherAvailabilityModel.end_time    >= slot_end_t,
                    ).first()
                    if not avail_ok:
                        continue

                if self.schedule_repo.check_conflict(
                    current_date, slot_start_t, slot_end_t,
                    teacher_id=teacher.id, cohort_id=cohort_id
                ):
                    continue

                room = None
                if available_rooms:
                    avail_r = self.schedule_repo.get_available_rooms(
                        current_date, slot_start_t, slot_end_t, available_rooms
                    )
                    if avail_r:
                        room = avail_r[0]

                slot = ScheduleSlotModel(
                    date        = current_date,
                    start_time  = slot_start_t,
                    end_time    = slot_end_t,
                    room        = room,
                    activity_id = activity.id,
                    teacher_id  = teacher.id,
                    cohort_id   = cohort_id,
                    delay_value = 0.0,
                    notes       = f'sporadic=True alpha=0.0 deadline={deadline}'
                )
                self.session.add(slot)
                scheduled_slots.append(slot)
                activity.hours_done = (activity.hours_done or 0) + slot_duration
                activity.status = ASE.IN_PROGRESS
                slots_needed -= 1
                break

            current_date += timedelta(days=1)

        if slots_needed == 0:
            activity.status = ASE.SCHEDULED

        self.session.commit()

        return {
            'success'         : True,
            'message'         : (
                f'Planification partielle : {len(scheduled_slots)} créneaux, {slots_needed} restants'
                if slots_needed > 0 else 'Tâche sporadique planifiée intégralement'
            ),
            'scheduled_slots' : len(scheduled_slots),
            'total_hours'     : len(scheduled_slots) * slot_duration,
            'conflicts'       : len(conflicts),
            'deadline'        : str(deadline),
            'test_acceptance' : test,
            'partial'         : slots_needed > 0,
        }

    def get_sporadic_tasks(self, cohort_id: int) -> List[Dict]:
        """Retourne toutes les tâches sporadiques d'une cohorte avec leur statut."""
        from src.database.models import AcademicActivityModel as AAM
        tasks = self.session.query(AAM).filter(
            AAM.cohort_id   == cohort_id,
            AAM.is_sporadic == True,
        ).all()

        result = []
        for t in tasks:
            deadline = None
            if getattr(t, 'arrival_date', None) and getattr(t, 'execution_window', None):
                deadline = t.arrival_date + timedelta(days=t.execution_window)
            remaining = max(0.0, t.volume_hours - (t.hours_done or 0))
            result.append({
                'id'              : t.id,
                'name'            : t.name,
                'code'            : t.code,
                'type'            : t.type.value if t.type else '',
                'volume_hours'    : t.volume_hours,
                'hours_done'      : t.hours_done or 0,
                'remaining'       : remaining,
                'arrival_date'    : str(t.arrival_date) if getattr(t, 'arrival_date', None) else None,
                'execution_window': getattr(t, 'execution_window', None),
                'deadline'        : str(deadline) if deadline else None,
                'status'          : t.status.value if t.status else '',
                'teacher_id'      : t.teacher_id,
            })
        return result