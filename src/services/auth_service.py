from functools import wraps
from typing import Callable, Optional
from sqlalchemy.orm import Session
from src.database.db_manager import db_manager


def _has_role(user, role_name: str) -> bool:
    if not user:
        return False
    try:
        return any(getattr(r,'name','').lower()==role_name.lower() for r in getattr(user,'roles',[]))
    except Exception:
        return False


def _has_permission(user, permission_name: str) -> bool:
    print(f"\n[DEBUG] _has_permission('{permission_name}') user={user} id={getattr(user,'id','?')}")
    if not user:
        print("[DEBUG] -> False: user None")
        return False
    if not hasattr(user, 'roles'):
        print("[DEBUG] -> False: pas de roles")
        return False
    try:
        session = db_manager.get_session()
        from src.database.models import UserModel
        fresh_user = session.query(UserModel).filter_by(id=user.id).first()
        print(f"[DEBUG] fresh_user={fresh_user}, id={getattr(fresh_user,'id','?')}")
        if fresh_user:
            for role in fresh_user.roles:
                print(f"[DEBUG]   role={role.name}")
                for p in role.permissions:
                    print(f"[DEBUG]     perm={p.name}")
                    if p.name.lower() == permission_name.lower():
                        print(f"[DEBUG] -> True")
                        return True
            print(f"[DEBUG] -> False: perm non trouvee")
            return False
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
    return False


OPEN_PERMISSIONS = {'submit_leave'}


def require_role(role_name: str) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.pop('current_user', None)
            if not _has_role(user, role_name):
                return {'success': False, 'error': 'Permission denied: role required'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission_name: str) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.pop('current_user', None)
            print(f"\n[DEBUG] require_permission('{permission_name}') user={user}")
            if permission_name in OPEN_PERMISSIONS:
                if user is None:
                    return {'success': False, 'error': 'Vous devez etre connecte.'}
                return func(*args, **kwargs)
            if not _has_permission(user, permission_name):
                return {'success': False, 'error': 'Permission denied: permission required'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def authenticate(identifier: str, password: str, session: Session = None):
    try:
        from src.database.models import UserModel
        from datetime import datetime
        s = session if session is not None else db_manager.get_session()
        user = s.query(UserModel).filter(
            (UserModel.username == identifier) | (UserModel.email == identifier)
        ).first()
        if user is None:
            return None, "Identifiant ou mot de passe incorrect."
        if getattr(user, "is_locked", False):
            return None, "Compte bloque apres trop de tentatives. Contactez l administrateur."
        if not user.is_active:
            return None, "Compte desactive. Contactez l administrateur."
        if verify_password(password, user.password_hash):
            user.login_attempts = 0
            user.is_locked = False
            s.commit()
            return user, None
        else:
            attempts = getattr(user, "login_attempts", 0) or 0
            attempts += 1
            user.login_attempts = attempts
            remaining = max(0, 3 - attempts)
            if attempts >= 3:
                user.is_locked = True
                user.locked_at = datetime.now()
                s.commit()
                return None, "Compte bloque apres 3 tentatives. Contactez l administrateur."
            else:
                s.commit()
                return None, f"Mot de passe incorrect. {remaining} tentative(s) restante(s)."
    except Exception as e:
        print(f"[auth_service] authenticate error: {e}")
        return None, "Erreur lors de la connexion."

def get_teacher_for_user(user):
    try:
        from src.database.models import TeacherModel
        session = db_manager.get_session()
        return session.query(TeacherModel).filter(TeacherModel.email == user.email).first()
    except Exception:
        return None

PASSWORD_MIN_LENGTH = 6

def create_user(username: str, email: str, password: str, session: Session = None):
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Mot de passe trop court")
    from src.database.models import UserModel
    close = False
    if session is None:
        session = db_manager.get_session()
        close = True
    try:
        existing = session.query(UserModel).filter(
            (UserModel.username == username) | (UserModel.email == email)
        ).first()
        if existing:
            return None
        user = UserModel(username=username, email=email,
                        password_hash=hash_password(password), is_active=True)
        session.add(user)
        session.commit()
        return user
    except ValueError:
        raise
    except Exception as e:
        session.rollback()
        return None
    finally:
        if close:
            session.close()