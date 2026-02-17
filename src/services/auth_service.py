"""
Simple authentication / authorization helpers (RBAC).

Provides `require_role` and `require_permission` decorators that expect
a `current_user` keyword argument (an ORM `UserModel` instance) to be passed
to protected methods.
"""
from functools import wraps
from typing import Callable
from sqlalchemy.orm import Session

from ..utils.passwords import hash_password, verify_password
from ..database.repositories import UserRepository, RoleRepository, PermissionRepository
from ..database.db_manager import db_manager

def _has_role(user, role_name: str) -> bool:
    if not user:
        return False
    return any(getattr(r, 'name', '').lower() == role_name.lower() for r in getattr(user, 'roles', []))

def _has_permission(user, permission_name: str) -> bool:
    if not user:
        return False
    for r in getattr(user, 'roles', []):
        for p in getattr(r, 'permissions', []):
            if getattr(p, 'name', '').lower() == permission_name.lower():
                return True
    return False


def require_role(role_name: str) -> Callable:
    """Decorator to require a role. The wrapped function must be called
    with a `current_user` kwarg containing the user object.
    Returns a permission-like dict when denied (keeps compatibility with
    existing manager return values).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not _has_role(user, role_name):
                return {'success': False, 'error': 'Permission denied: role required'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission_name: str) -> Callable:
    """Decorator to require a specific permission (by name).
    The wrapped function must be called with `current_user` kwarg.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not _has_permission(user, permission_name):
                return {'success': False, 'error': 'Permission denied: permission required'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def create_user(username: str, email: str, password: str, session: Session = None):
    """Create a new user with hashed password. Returns the UserModel."""
    close = False
    if session is None:
        session = db_manager.get_session()
        close = True

    try:
        user_repo = UserRepository(session)
        existing = user_repo.get_by_username(username) or user_repo.get_by_email(email)
        if existing:
            return None

        pw_hash = hash_password(password)
        user = user_repo.create(username=username, email=email, password_hash=pw_hash)
        return user
    finally:
        if close:
            session.close()


def authenticate(identifier: str, password: str, session: Session = None):
    """Authenticate by username or email. Returns user or None."""
    close = False
    if session is None:
        session = db_manager.get_session()
        close = True

    try:
        user_repo = UserRepository(session)
        user = user_repo.get_by_username(identifier) or user_repo.get_by_email(identifier)
        if not user:
            return None

        if verify_password(password, user.password_hash):
            return user
        return None
    finally:
        if close:
            session.close()


def get_teacher_for_user(user, session: Session = None):
    """
    Retourne l'enseignant associé à l'utilisateur (par teacher_id ou par email).
    Utile pour le rôle Enseignant.
    """
    if not user:
        return None
    close = False
    if session is None:
        session = db_manager.get_session()
        close = True
    try:
        from ..database.repositories import TeacherRepository
        teacher_repo = TeacherRepository(session)
        if getattr(user, 'teacher_id', None):
            return teacher_repo.get_by_id(user.teacher_id)
        return teacher_repo.get_by_email(user.email)
    finally:
        if close:
            session.close()

