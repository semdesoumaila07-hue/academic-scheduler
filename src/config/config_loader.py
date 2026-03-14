"""
Chargeur de configuration JSON.

Charge et gère les fichiers de configuration JSON.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    Chargeur de configuration depuis fichiers JSON.
    
    Attributes:
        config_dir: Répertoire contenant les fichiers de config
    """
    
    def __init__(self, config_dir: Path = None):
        """
        Initialise le chargeur de configuration.
        
        Args:
            config_dir: Répertoire de configuration (config/ par défaut)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.config_dir = config_dir
        self._app_config: Optional[Dict[str, Any]] = None
        self._algorithm_params: Optional[Dict[str, Any]] = None
    
    def load_app_config(self) -> Dict[str, Any]:
        """
        Charge la configuration de l'application.
        
        Returns:
            Dictionnaire de configuration
        """
        if self._app_config is None:
            config_file = self.config_dir / "app_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._app_config = json.load(f)
            else:
                # Configuration par défaut si le fichier n'existe pas
                self._app_config = self._get_default_app_config()
        
        return self._app_config
    
    def load_algorithm_params(self) -> Dict[str, Any]:
        """
        Charge les paramètres de l'algorithme Pfair.
        
        Returns:
            Dictionnaire de paramètres
        """
        if self._algorithm_params is None:
            params_file = self.config_dir / "algorithm_params.json"
            
            if params_file.exists():
                with open(params_file, 'r', encoding='utf-8') as f:
                    self._algorithm_params = json.load(f)
            else:
                # Paramètres par défaut
                self._algorithm_params = self._get_default_algorithm_params()
        
        return self._algorithm_params
    
    def get(self, key: str, default: Any = None, config_type: str = 'app') -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration (ex: "database.auto_backup")
            default: Valeur par défaut si la clé n'existe pas
            config_type: Type de config ('app' ou 'algorithm')
            
        Returns:
            Valeur de configuration
        """
        if config_type == 'app':
            config = self.load_app_config()
        else:
            config = self.load_algorithm_params()
        
        # Navigation dans le dictionnaire avec des clés séparées par des points
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """Recharge les configurations depuis les fichiers."""
        self._app_config = None
        self._algorithm_params = None
    
    def _get_default_app_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut de l'application."""
        return {
            "application": {
                "name": "Système d'Ordonnancement Académique",
                "version": "1.0.0"
            },
            "database": {
                "type": "sqlite",
                "filename": "ordonnancement.db",
                "path": "data/ordonnancement.db"
            },
            "logging": {
                "enabled": True,
                "level": "INFO"
            }
        }
    
    def _get_default_algorithm_params(self) -> Dict[str, Any]:
        """Retourne les paramètres par défaut de l'algorithme."""
        return {
            "pfair": {
                "thresholds": {
                    "max_total_charge": 1.0,
                    "urgent_alpha": 1.0,
                    "important_alpha": 0.5
                },
                "scheduling": {
                    "slot_duration_hours": 2,
                    "max_slots_per_day": 4
                }
            }
        }


# Instance globale
config_loader = ConfigLoader()