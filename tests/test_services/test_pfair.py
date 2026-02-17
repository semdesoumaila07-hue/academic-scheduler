"""
Tests unitaires pour le service PfairScheduler.
"""
import pytest
from datetime import date, time
from unittest.mock import Mock, MagicMock
from src.services import PfairScheduler


class TestPfairScheduler:
    """Tests pour PfairScheduler."""
    
    @pytest.fixture
    def mock_session(self):
        """Crée une session mock."""
        return Mock()
    
    @pytest.fixture
    def scheduler(self, mock_session):
        """Crée une instance de PfairScheduler."""
        return PfairScheduler(mock_session)
    
    def test_calculate_activity_priority(self, scheduler):
        """Test calcul de priorité d'une activité."""
        activity = Mock()
        activity.charge_factor = 0.5
        activity.hours_done = 10
        
        # t = 30 jours
        alpha, delay = scheduler.calculate_activity_priority(activity, 30)
        
        # Attendu: delay = 0.5 * 30 - 10 = 5
        #          alpha = 5 / 0.5 = 10
        assert delay == 5.0
        assert alpha == 10.0
    
    def test_calculate_priority_zero_charge(self, scheduler):
        """Test avec facteur de charge nul."""
        activity = Mock()
        activity.charge_factor = 0
        activity.hours_done = 0
        
        alpha, delay = scheduler.calculate_activity_priority(activity, 10)
        
        assert alpha == 0.0
        assert delay == 0.0
    
    def test_is_schedulable_feasible(self, scheduler, mock_session):
        """Test de faisabilité avec charge acceptable."""
        # Mock des activités
        activity1 = Mock()
        activity1.volume_hours = 30
        activity1.hours_done = 0
        
        activity2 = Mock()
        activity2.volume_hours = 20
        activity2.hours_done = 0
        
        scheduler.activity_repo = Mock()
        scheduler.activity_repo.get_by_cohort.return_value = [activity1, activity2]
        
        scheduler.calendar_service = Mock()
        scheduler.calendar_service.calculate_effective_days.return_value = 100
        
        result = scheduler.is_schedulable(1, date(2026, 1, 1), date(2026, 3, 31))
        
        # Charge = (30 + 20) / 100 = 0.5 ≤ 1.0
        assert result['schedulable'] is True
        assert result['total_charge'] == 0.5
    
    def test_is_schedulable_overloaded(self, scheduler, mock_session):
        """Test de faisabilité avec surcharge."""
        activity1 = Mock()
        activity1.volume_hours = 80
        activity1.hours_done = 0
        
        activity2 = Mock()
        activity2.volume_hours = 60
        activity2.hours_done = 0
        
        scheduler.activity_repo = Mock()
        scheduler.activity_repo.get_by_cohort.return_value = [activity1, activity2]
        
        scheduler.calendar_service = Mock()
        scheduler.calendar_service.calculate_effective_days.return_value = 100
        
        result = scheduler.is_schedulable(1, date(2026, 1, 1), date(2026, 3, 31))
        
        # Charge = (80 + 60) / 100 = 1.4 > 1.0
        assert result['schedulable'] is False
        assert result['total_charge'] == 1.4