"""
Repository pour les utilisateurs.
"""
from typing import Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import UserModel


class UserRepository(BaseRepository[UserModel]):
    """Repository pour les opérations sur les utilisateurs."""

    def __init__(self, session: Session):
        super().__init__(UserModel, session)

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.first_by(username=username)

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.first_by(email=email)

    def add_role(self, user: UserModel, role) -> UserModel:
        if role not in user.roles:
            user.roles.append(role)
            self.session.commit()
            self.session.refresh(user)
        return user
