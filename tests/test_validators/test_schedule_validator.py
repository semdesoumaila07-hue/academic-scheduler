"""
Tests pour ScheduleValidator.
"""
import pytest
from datetime import time, date
from src.validators import ScheduleValidator


class TestScheduleValidator:
    """Tests pour ScheduleValidator."""
    
    def test_validate_time_slot_valid(self):
        """Test validation créneau valide."""
        valid, error = ScheduleValidator.validate_time_slot(
            time(8, 0),
            time(10, 0)
        )
        
        assert valid is True
        assert error is None
    
    def test_validate_time_slot_invalid_order(self):
        """Test avec heure fin avant heure début."""
        valid, error = ScheduleValidator.validate_time_slot(
            time(10, 0),
            time(8, 0)
        )
        
        assert valid is False
        assert "après" in error.lower()
    
    def test_validate_time_slot_too_short(self):
        """Test durée trop courte."""
        valid, error = ScheduleValidator.validate_time_slot(
            time(8, 0),
            time(8, 15)  # 15 minutes
        )
        
        assert valid is False
        assert "30 minutes" in error
    
    def test_validate_time_slot_too_long(self):
        """Test durée trop longue."""
        valid, error = ScheduleValidator.validate_time_slot(
            time(8, 0),
            time(13, 0)  # 5 heures
        )
        
        assert valid is False
        assert "4 heures" in error
    
    def test_validate_time_slot_outside_hours(self):
        """Test horaires hors plage de travail."""
        valid, error = ScheduleValidator.validate_time_slot(
            time(6, 0),  # Avant 7h
            time(8, 0)
        )
        
        assert valid is False
        assert "7h et 20h" in error
    
    def test_validate_room_valid(self):
        """Test validation salle valide."""
        valid, error = ScheduleValidator.validate_room("A101")
        
        assert valid is True
        assert error is None
    
    def test_validate_room_empty(self):
        """Test salle vide."""
        valid, error = ScheduleValidator.validate_room("")
        
        assert valid is False
        assert "vide" in error.lower()
    
    def test_validate_room_too_long(self):
        """Test nom de salle trop long."""
        long_name = "A" * 60
        valid, error = ScheduleValidator.validate_room(long_name)
        
        assert valid is False
        assert "50 caractères" in error