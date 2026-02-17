"""
Repository de base avec les opérations CRUD génériques.
"""
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import Base

# Type générique pour le modèle
ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repository de base implémentant les opérations CRUD standard.
    
    Attributes:
        model: Classe du modèle SQLAlchemy
        session: Session de base de données
    """
    
    def __init__(self, model: Type[ModelType], session: Session):
        """
        Initialise le repository.
        
        Args:
            model: Classe du modèle SQLAlchemy
            session: Session de base de données
        """
        self.model = model
        self.session = session
    
    def create(self, **kwargs) -> ModelType:
        """
        Crée une nouvelle instance dans la base de données.
        
        Args:
            **kwargs: Attributs de l'instance
            
        Returns:
            Instance créée
        """
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Récupère une instance par son ID.
        
        Args:
            id: Identifiant
            
        Returns:
            Instance trouvée ou None
        """
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Récupère toutes les instances.
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste des instances
        """
        return self.session.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Met à jour une instance.
        
        Args:
            id: Identifiant de l'instance
            **kwargs: Attributs à mettre à jour
            
        Returns:
            Instance mise à jour ou None
        """
        try:
            instance = self.get_by_id(id)
            if instance is None:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def delete(self, id: int) -> bool:
        """
        Supprime une instance.
        
        Args:
            id: Identifiant de l'instance
            
        Returns:
            True si supprimé, False sinon
        """
        try:
            instance = self.get_by_id(id)
            if instance is None:
                return False
            
            self.session.delete(instance)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def count(self) -> int:
        """
        Compte le nombre total d'instances.
        
        Returns:
            Nombre d'instances
        """
        return self.session.query(self.model).count()
    
    def exists(self, id: int) -> bool:
        """
        Vérifie si une instance existe.
        
        Args:
            id: Identifiant
            
        Returns:
            True si existe, False sinon
        """
        return self.session.query(self.model).filter(self.model.id == id).count() > 0
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """
        Filtre les instances par attributs.
        
        Args:
            **kwargs: Critères de filtrage
            
        Returns:
            Liste des instances filtrées
        """
        return self.session.query(self.model).filter_by(**kwargs).all()
    
    def first_by(self, **kwargs) -> Optional[ModelType]:
        """
        Retourne la première instance correspondant aux critères.
        
        Args:
            **kwargs: Critères de filtrage
            
        Returns:
            Première instance ou None
        """
        return self.session.query(self.model).filter_by(**kwargs).first()