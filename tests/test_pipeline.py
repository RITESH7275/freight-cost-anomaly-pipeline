"""
Unit tests for Freight Tiger Anomaly Detection Pipeline.
Validates metric accuracy, baseline calculations, and note matching.
"""

import unittest
import pandas as pd
from src.metrics import calculate_weekly_metrics, compute_baselines
from src.matcher import find_explanation

class TestFreightPipeline(unittest.TestCase):

    def setUp(self):
        """Set up mock shipment and context note data for testing."""
        self.mock_shipments = pd.DataFrame([
            {
                'shipment_id': 'SHP00001',
                'origin': 'Mumbai',
                'destination': 'Pune',
                'route': 'Mumbai-Pune',
                'route_type': 'Short',
                'quantity_tonnes': 10.0,
                'distance_km': 100.0,
                'freight_cost_inr': 3000, # 3000 / 1000 = 3.0 cost_per_tonne_km
                'shipment_date': pd.to_datetime('2025-01-06'),
                'week_of': pd.to_datetime('2025-01-06')
            }
        ])

        self.mock_notes = pd.DataFrame([
            {
                'note_id': 'N001',
                'date': pd.to_datetime('2025-01-06'),
                'applies_to': 'Mumbai-Pune',
                'note': 'Heavy flooding forced detours and higher trip costs.'
            }
        ])

    def test_calculate_weekly_metrics(self):
        """Test unit economics calculation (cost per tonne-km)."""
        weekly_df = calculate_weekly_metrics(self.mock_shipments)
        self.assertIn('cost_per_tonne_km', weekly_df.columns)
        calculated_rate = weekly_df.loc[0, 'cost_per_tonne_km']
        self.assertAlmostEqual(calculated_rate, 3.0, places=2) # type: ignore

    def test_find_explanation_match(self):
        """Test context note matching when a spike occurs."""
        matched, closest = find_explanation(
            route='Mumbai-Pune',
            week_start=pd.to_datetime('2025-01-06'),
            notes=self.mock_notes,
            window_days=14
        )
        self.assertIsNotNone(matched)
        self.assertEqual(matched['note_id'], 'N001') # type: ignore

if __name__ == '__main__':
    unittest.main()