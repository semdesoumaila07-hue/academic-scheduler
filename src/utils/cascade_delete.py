"""
cascade_delete.py — Fonctions de suppression sécurisée avec gestion
des dépendances SQLite (clés étrangères).

Toutes les fonctions suivent le même pattern :
  1. Supprimer les enregistrements fils (dans le bon ordre)
  2. Supprimer l'enregistrement parent
  3. commit() en cas de succès, rollback() en cas d'erreur

Usage depuis n'importe quel onglet ou manager :
    from src.utils.cascade_delete import delete_teacher, delete_activity
    result = delete_teacher(session, teacher_id)
    if not result['success']:
        QMessageBox.critical(self, "Erreur", result['error'])
"""
from sqlalchemy.orm import Session


def delete_teacher(session: Session, teacher_id: int) -> dict:
    """
    Supprime un enseignant en gérant toutes ses dépendances :
      - Détache ses activités (teacher_id → NULL)
      - Supprime ses créneaux horaires
      - Supprime ses disponibilités
      - Supprime ses demandes de congé
      - Supprime ses signalements de contrainte
      - Supprime l'enseignant lui-même
    """
    try:
        from ..database.models import (
            TeacherModel, AcademicActivityModel, ScheduleSlotModel,
            TeacherAvailabilityModel, LeaveRequestModel
        )

        teacher = session.query(TeacherModel).filter_by(id=teacher_id).first()
        if not teacher:
            return {'success': False, 'error': 'Enseignant introuvable'}

        # 1. Détacher les activités (on ne les supprime pas — elles restent
        #    dans la cohorte, juste sans enseignant assigné)
        session.query(AcademicActivityModel).filter(
            AcademicActivityModel.teacher_id == teacher_id
        ).update({'teacher_id': None}, synchronize_session=False)

        # 2. Supprimer les créneaux horaires de l'enseignant
        session.query(ScheduleSlotModel).filter(
            ScheduleSlotModel.teacher_id == teacher_id
        ).delete(synchronize_session=False)

        # 3. Supprimer les disponibilités
        session.query(TeacherAvailabilityModel).filter(
            TeacherAvailabilityModel.teacher_id == teacher_id
        ).delete(synchronize_session=False)

        # 4. Supprimer les demandes de congé
        session.query(LeaveRequestModel).filter(
            LeaveRequestModel.teacher_id == teacher_id
        ).delete(synchronize_session=False)

        # 5. Supprimer les signalements de contrainte (si le modèle existe)
        try:
            from ..database.models import ConstraintReportModel
            session.query(ConstraintReportModel).filter(
                ConstraintReportModel.teacher_id == teacher_id
            ).delete(synchronize_session=False)
        except (ImportError, Exception):
            pass

        # 6. Supprimer l'enseignant
        session.delete(teacher)
        session.commit()

        return {
            'success': True,
            'message': f'Enseignant {teacher.full_name} supprimé avec succès'
        }

    except Exception as e:
        session.rollback()
        return {'success': False, 'error': f'Impossible de supprimer l\'enseignant : {e}'}


def delete_activity(session: Session, activity_id: int) -> dict:
    """
    Supprime une activité en gérant ses créneaux horaires associés.
    """
    try:
        from ..database.models import AcademicActivityModel, ScheduleSlotModel

        activity = session.query(AcademicActivityModel).filter_by(
            id=activity_id
        ).first()
        if not activity:
            return {'success': False, 'error': 'Activité introuvable'}

        # 1. Supprimer les créneaux horaires liés à cette activité
        session.query(ScheduleSlotModel).filter(
            ScheduleSlotModel.activity_id == activity_id
        ).delete(synchronize_session=False)

        # 2. Supprimer l'activité
        session.delete(activity)
        session.commit()

        return {
            'success': True,
            'message': f'Activité {activity.name} supprimée avec succès'
        }

    except Exception as e:
        session.rollback()
        return {'success': False, 'error': f'Impossible de supprimer l\'activité : {e}'}


def delete_schedule_slot(session: Session, slot_id: int) -> dict:
    """Supprime un créneau horaire."""
    try:
        from ..database.models import ScheduleSlotModel

        slot = session.query(ScheduleSlotModel).filter_by(id=slot_id).first()
        if not slot:
            return {'success': False, 'error': 'Créneau introuvable'}

        session.delete(slot)
        session.commit()
        return {'success': True, 'message': 'Créneau supprimé avec succès'}

    except Exception as e:
        session.rollback()
        return {'success': False, 'error': f'Impossible de supprimer le créneau : {e}'}