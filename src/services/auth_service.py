"""
Service d'authentification et de gestion des permissions.
Utilise bcrypt pour le hachage sécurisé des mots de passe.
"""
import bcrypt
from functools import wraps
from typing import Callable, Optional
from sqlalchemy.orm import Session
from src.database.db_manager import db_manager


def _has_role(user, role_name: str) -> bool:
    if not user:
        return False
    try:
        return any(getattr(r, 'name', '').lower() == role_name.lower()
                   for r in getattr(user, 'roles', []))
    except Exception:
        return False


def _has_permission(user, permission_name: str) -> bool:
    if not user:
        return False
    if not hasattr(user, 'roles'):
        return False
    try:
        session = db_manager.get_session()
        from src.database.models import UserModel
        fresh_user = session.query(UserModel).filter_by(id=user.id).first()
        if fresh_user:
            for role in fresh_user.roles:
                for p in role.permissions:
                    if p.name.lower() == permission_name.lower():
                        return True
        return False
    except Exception as e:
        print(f"[auth_service] _has_permission error: {e}")
    return False


OPEN_PERMISSIONS = {'submit_leave'}


def require_role(role_name: str) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.pop('current_user', None)
            if not _has_role(user, role_name):
                return {'success': False, 'error': 'Permission refusée : rôle requis'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission_name: str) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.pop('current_user', None)
            if permission_name in OPEN_PERMISSIONS:
                if user is None:
                    return {'success': False, 'error': 'Vous devez être connecté.'}
                return func(*args, **kwargs)
            if not _has_permission(user, permission_name):
                return {'success': False, 'error': 'Permission refusée'}
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ── Hachage bcrypt ─────────────────────────────────────────────────────────
# bcrypt génère automatiquement un sel aléatoire à chaque appel.
# Le sel est stocké dans le hash lui-même — pas besoin de le sauvegarder séparément.
# work_factor=12 : bon équilibre sécurité/performance (≈ 250 ms sur CPU moderne).

BCRYPT_WORK_FACTOR = 12


def hash_password(password: str) -> str:
    """
    Hache un mot de passe en clair avec bcrypt.

    Args:
        password: Mot de passe en clair

    Returns:
        Hash bcrypt sous forme de chaîne (inclut le sel et le facteur de coût)
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=BCRYPT_WORK_FACTOR)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Vérifie un mot de passe en clair contre un hash bcrypt stocké.

    Args:
        plain: Mot de passe en clair saisi par l'utilisateur
        hashed: Hash bcrypt stocké en base de données

    Returns:
        True si le mot de passe est correct, False sinon
    """
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ── Authentification ────────────────────────────────────────────────────────

def authenticate(identifier: str, password: str, session: Session = None):
    """
    Authentifie un utilisateur par identifiant (email ou nom d'utilisateur) et mot de passe.

    Args:
        identifier: Email ou nom d'utilisateur
        password: Mot de passe en clair
        session: Session SQLAlchemy (optionnel)

    Returns:
        Tuple (user, error_message) — user est None en cas d'échec
    """
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
            return None, "Compte bloqué après trop de tentatives. Contactez l'administrateur."

        if not user.is_active:
            return None, "Compte désactivé. Contactez l'administrateur."

        if verify_password(password, user.password_hash):
            # Connexion réussie — réinitialise le compteur de tentatives
            user.login_attempts = 0
            user.is_locked = False
            s.commit()
            return user, None
        else:
            # Mot de passe incorrect — incrémente le compteur
            attempts = getattr(user, "login_attempts", 0) or 0
            attempts += 1
            user.login_attempts = attempts
            remaining = max(0, 3 - attempts)

            if attempts >= 3:
                user.is_locked = True
                user.locked_at = datetime.now()
                s.commit()
                return None, "Compte bloqué après 3 tentatives échouées. Contactez l'administrateur."
            else:
                s.commit()
                return None, f"Mot de passe incorrect. {remaining} tentative(s) restante(s)."

    except Exception as e:
        print(f"[auth_service] authenticate error: {e}")
        return None, "Erreur lors de la connexion."


def get_teacher_for_user(user):
    """Retourne le TeacherModel lié à un UserModel via l'email."""
    try:
        from src.database.models import TeacherModel
        session = db_manager.get_session()
        return session.query(TeacherModel).filter(
            TeacherModel.email == user.email
        ).first()
    except Exception:
        return None


PASSWORD_MIN_LENGTH = 8


def create_user(username: str, email: str, password: str, session: Session = None):
    """
    Crée un nouvel utilisateur avec mot de passe haché par bcrypt.

    Args:
        username: Nom d'utilisateur
        email: Adresse email
        password: Mot de passe en clair (min 8 caractères)
        session: Session SQLAlchemy (optionnel)

    Returns:
        UserModel créé, ou None si l'utilisateur existe déjà
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Mot de passe trop court (minimum {PASSWORD_MIN_LENGTH} caractères)")

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

        user = UserModel(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True
        )
        session.add(user)
        session.commit()
        return user

    except ValueError:
        raise
    except Exception as e:
        session.rollback()
        print(f"[auth_service] create_user error: {e}")
        return None
    finally:
        if close:
            session.close()