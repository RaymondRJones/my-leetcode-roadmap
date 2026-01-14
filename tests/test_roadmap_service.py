"""
Tests for RoadmapService.
"""
import pytest
from app.services.roadmap_service import RoadmapService


class TestRoadmapServiceInit:
    """Tests for RoadmapService initialization."""

    def test_service_initializes(self):
        """Test that RoadmapService initializes correctly."""
        service = RoadmapService(
            month_order=['April', 'May'],
            month_mapping={'April': 'Month 1', 'May': 'Month 2'},
            intermediate_month_order=['Month 1', 'Month 2']
        )
        assert service is not None
        assert service.month_order == ['April', 'May']
        assert service.month_mapping == {'April': 'Month 1', 'May': 'Month 2'}

    def test_service_loads_data(self, app_context, app):
        """Test that service loads data from app."""
        service = app.roadmap
        assert service is not None
        # Data may or may not exist, but service should handle gracefully
        assert isinstance(service.roadmap_data, dict)
        assert isinstance(service.intermediate_roadmap_data, dict)
        assert isinstance(service.atcoder_problems, dict)


class TestRoadmapServiceMethods:
    """Tests for RoadmapService methods."""

    def test_get_ordered_roadmap_data(self, app_context, app):
        """Test get_ordered_roadmap_data returns dict."""
        service = app.roadmap
        data = service.get_ordered_roadmap_data()
        assert isinstance(data, dict)

    def test_get_ordered_intermediate_roadmap_data(self, app_context, app):
        """Test get_ordered_intermediate_roadmap_data returns dict."""
        service = app.roadmap
        data = service.get_ordered_intermediate_roadmap_data()
        assert isinstance(data, dict)

    def test_get_atcoder_problems(self, app_context, app):
        """Test get_atcoder_problems returns dict."""
        service = app.roadmap
        data = service.get_atcoder_problems()
        assert isinstance(data, dict)

    def test_get_all_problems(self, app_context, app):
        """Test get_all_problems returns list."""
        service = app.roadmap
        data = service.get_all_problems()
        assert isinstance(data, list)

    def test_get_original_month_name(self, app_context, app):
        """Test get_original_month_name conversion."""
        service = app.roadmap
        # Test known mapping
        original = service.get_original_month_name('Month 1')
        assert original == 'April'

        # Test unknown mapping returns input
        unknown = service.get_original_month_name('Unknown')
        assert unknown == 'Unknown'


class TestRoadmapDataProcessing:
    """Tests for roadmap data processing."""

    def test_process_month_data_handles_bonus(self):
        """Test that day 30 becomes bonus section."""
        service = RoadmapService(
            month_order=['April'],
            month_mapping={'April': 'Month 1'},
            intermediate_month_order=['Month 1']
        )

        month_data = [
            {'day': 1, 'problems': [{'name': 'Problem 1'}]},
            {'day': 30, 'problems': [{'name': 'Bonus Problem'}]}
        ]

        processed = service._process_month_data(month_data)

        # Should have day 1 and bonus section
        assert len(processed) == 2
        day_numbers = [d['day'] for d in processed]
        assert 1 in day_numbers
        assert 'bonus' in day_numbers

    def test_process_month_data_limits_problems_per_day(self):
        """Test that days are limited to 3 problems."""
        service = RoadmapService(
            month_order=['April'],
            month_mapping={'April': 'Month 1'},
            intermediate_month_order=['Month 1']
        )

        month_data = [
            {'day': 1, 'problems': [
                {'name': f'Problem {i}'} for i in range(5)
            ]}
        ]

        processed = service._process_month_data(month_data)

        # Day 1 should have max 3 problems
        day_1 = next(d for d in processed if d['day'] == 1)
        assert len(day_1['problems']) == 3

        # Overflow should go to bonus
        bonus = next((d for d in processed if d['day'] == 'bonus'), None)
        assert bonus is not None
        assert len(bonus['problems']) == 2


class TestRoadmapServiceIntegration:
    """Integration tests for RoadmapService with app."""

    def test_api_roadmap_uses_service(self, client):
        """Test that API endpoint uses roadmap service."""
        response = client.get('/api/roadmap')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    def test_api_atcoder_uses_service(self, client):
        """Test that API endpoint uses roadmap service."""
        response = client.get('/api/atcoder')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)

    def test_beginner_page_uses_service(self, client):
        """Test that beginner page gets data from service."""
        response = client.get('/beginner')
        assert response.status_code == 200

    def test_intermediate_page_uses_service(self, client):
        """Test that intermediate page gets data from service."""
        response = client.get('/intermediate')
        assert response.status_code == 200
