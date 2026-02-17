"""
Package des dialogues de l'interface utilisateur.
"""

from .teacher_dialog import TeacherDialog
from .activity_dialog import ActivityDialog
from .leave_request_dialog import LeaveRequestDialog
from .schedule_viewer import ScheduleViewer

__all__ = [
    'TeacherDialog',
    'ActivityDialog',
    'LeaveRequestDialog',
    'ScheduleViewer',
]