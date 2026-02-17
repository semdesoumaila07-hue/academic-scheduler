"""
Tests unitaires pour l'entité AcademicActivity.
"""
import pytest
from datetime import date, timedelta
from src.entities import AcademicActivity
from src.utils.constants import ActivityTypeEnum


class TestAcademicActivity:
    """Tests pour AcademicActivity."""
    
    def test_create_activity_valid(self):
        """Test création d'une activité valide."""
        activity = AcademicActivity(
            name="Algorithmique",
            code="ALGO-301",
            type=ActivityTypeEnum.COURS,
            volume_hours=30,
            cohort_id=1,
            teacher_id=1
        )
        
        assert activity.name == "Algorithmique"
        assert activity.code == "ALGO-301"
        assert activity.volume_hours == 30
        assert activity.hours_done == 0
    
    def test_validate_success(self):
        """Test validation réussie."""
        activity = AcademicActivity(
            name="Bases de données",
            code="BD-301",
            type=ActivityTypeEnum.COURS,
            volume_hours=25,
            cohort_id=1
        )
        
        is_valid, error = activity.validate()
        assert is_valid is True
        assert error is None
    
    def test_validate_empty_name(self):
        """Test validation avec nom vide."""
        activity = AcademicActivity(
            name="",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=20,
            cohort_id=1
        )
        
        is_valid, error = activity.validate()
        assert is_valid is False
        assert "nom" in error.lower()
    
    def test_validate_invalid_volume(self):
        """Test validation avec volume négatif."""
        activity = AcademicActivity(
            name="Test",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=-10,
            cohort_id=1
        )
        
        is_valid, error = activity.validate()
        assert is_valid is False
        assert "volume" in error.lower()
    
    def test_calculate_charge_factor(self):
        """Test calcul du facteur de charge."""
        activity = AcademicActivity(
            name="Test",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=30,
            cohort_id=1
        )
        
        # D_effectif = 60 jours
        activity.calculate_charge_factor(60)
        
        assert activity.charge_factor == 0.5  # 30/60
    
    def test_update_hours(self):
        """Test mise à jour des heures."""
        activity = AcademicActivity(
            name="Test",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=30,
            cohort_id=1
        )
        
        activity.add_hours(10)
        assert activity.hours_done == 10
        
        activity.add_hours(5)
        assert activity.hours_done == 15
    
    def test_get_remaining_hours(self):
        """Test calcul des heures restantes."""
        activity = AcademicActivity(
            name="Test",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=30,
            cohort_id=1
        )
        
        activity.hours_done = 10
        assert activity.get_remaining_hours() == 20
    
    def test_get_completion_percentage(self):
        """Test calcul du pourcentage de complétion."""
        activity = AcademicActivity(
            name="Test",
            code="TEST-001",
            type=ActivityTypeEnum.COURS,
            volume_hours=30,
            cohort_id=1
        )
        
        activity.hours_done = 15
        assert activity.get_completion_percentage() == 50.0