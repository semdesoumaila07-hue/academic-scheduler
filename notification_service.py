# -*- coding: utf-8 -*-
"""
notification_service.py — Service de notifications
Chemin : src/services/notification_service.py
"""
from datetime import datetime
from src.database.db_manager import db_manager
from sqlalchemy import text


def create_notification(user_id: int, title: str, message: str, notif_type: str = 'info'):
    """
    Crée une notification pour un utilisateur.
    notif_type: 'info', 'success', 'warning', 'danger'
    """
    try:
        session = db_manager.get_session()
        session.execute(text("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (:uid, :title, :msg, :type, 0, :now)
        """), {
            'uid': user_id,
            'title': title,
            'msg': message,
            'type': notif_type,
            'now': datetime.now().isoformat()
        })
        session.commit()
    except Exception as e:
        print(f"[notification_service] create error: {e}")


def get_notifications(user_id: int, unread_only: bool = False):
    """Retourne les notifications d'un utilisateur."""
    try:
        session = db_manager.get_session()
        query = "SELECT * FROM notifications WHERE user_id = :uid"
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_at DESC LIMIT 50"
        result = session.execute(text(query), {'uid': user_id})
        return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"[notification_service] get error: {e}")
        return []


def mark_as_read(notif_id: int):
    """Marque une notification comme lue."""
    try:
        session = db_manager.get_session()
        session.execute(text("UPDATE notifications SET is_read = 1 WHERE id = :id"), {'id': notif_id})
        session.commit()
    except Exception as e:
        print(f"[notification_service] mark_read error: {e}")


def mark_all_read(user_id: int):
    """Marque toutes les notifications d'un utilisateur comme lues."""
    try:
        session = db_manager.get_session()
        session.execute(text("UPDATE notifications SET is_read = 1 WHERE user_id = :uid"), {'uid': user_id})
        session.commit()
    except Exception as e:
        print(f"[notification_service] mark_all error: {e}")


def count_unread(user_id: int) -> int:
    """Retourne le nombre de notifications non lues."""
    try:
        session = db_manager.get_session()
        result = session.execute(text(
            "SELECT COUNT(*) FROM notifications WHERE user_id = :uid AND is_read = 0"
        ), {'uid': user_id})
        return result.scalar() or 0
    except Exception as e:
        print(f"[notification_service] count error: {e}")
        return 0


def notify_leave_approved(leave_request_id: int, teacher_user_id: int, teacher_name: str):
    """Notifie l'enseignant que son congé a été approuvé."""
    create_notification(
        user_id=teacher_user_id,
        title="Congé approuvé ✅",
        message=f"Votre demande de congé a été approuvée.",
        notif_type='success'
    )


def notify_leave_rejected(leave_request_id: int, teacher_user_id: int, reason: str = ""):
    """Notifie l'enseignant que son congé a été refusé."""
    msg = "Votre demande de congé a été refusée."
    if reason:
        msg += f" Motif : {reason}"
    create_notification(
        user_id=teacher_user_id,
        title="Congé refusé ❌",
        message=msg,
        notif_type='danger'
    )


def check_urgent_activities():
    """Vérifie les activités urgentes (α ≥ 0.8) et crée des notifications pour les admins."""
    try:
        session = db_manager.get_session()
        # Récupérer les activités avec lag_ratio calculé
        activities = session.execute(text("""
            SELECT a.id, a.name, a.volume_hours,
                   COALESCE(SUM(s.duration_hours), 0) as scheduled_hours
            FROM activities a
            LEFT JOIN schedule_slots s ON s.activity_id = a.id
            GROUP BY a.id
        """)).fetchall()

        # Récupérer les admins
        admins = session.execute(text("""
            SELECT DISTINCT u.id FROM users u
            JOIN user_roles ur ON ur.user_id = u.id
            JOIN roles r ON r.id = ur.role_id
            WHERE r.name IN ('Admin', 'admin')
        """)).fetchall()
        admin_ids = [row[0] for row in admins]

        for act in activities:
            volume = act[2] or 0
            scheduled = act[3] or 0
            if volume <= 0:
                continue
            alpha = scheduled / volume if volume > 0 else 0
            lag = 1 - alpha  # lag_ratio = 1 - (scheduled/volume)

            for admin_id in admin_ids:
                # Vérifier si notification déjà envoyée récemment
                existing = session.execute(text("""
                    SELECT id FROM notifications
                    WHERE user_id = :uid AND title LIKE :title AND is_read = 0
                """), {'uid': admin_id, 'title': f"%{act[1]}%"}).fetchone()

                if existing:
                    continue

                if lag >= 1.0:
                    create_notification(
                        user_id=admin_id,
                        title=f"🚨 Activité critique : {act[1]}",
                        message=f"L'activité '{act[1]}' a un retard critique (α ≥ 1). Aucune heure planifiée sur {volume}h.",
                        notif_type='danger'
                    )
                elif lag >= 0.8:
                    create_notification(
                        user_id=admin_id,
                        title=f"⚠️ Activité urgente : {act[1]}",
                        message=f"L'activité '{act[1]}' approche du seuil critique (α ≥ 0.8). Seulement {scheduled}h/{volume}h planifiées.",
                        notif_type='warning'
                    )
    except Exception as e:
        print(f"[notification_service] check_urgent error: {e}")