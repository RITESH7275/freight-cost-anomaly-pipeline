"""
Configuration settings for Freight Tiger logistics anomaly detector.
Centralizes paths, spike thresholds, and matching parameters.
"""

from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

SHIPMENTS_PATH = DATA_DIR / "shipment_records.csv"
NOTES_PATH = DATA_DIR / "context_notes.csv"
OUTPUT_PATH = DATA_DIR / "final_output.csv"

# Anomaly detection thresholds (%)
HISTORICAL_SPIKE_THRESHOLD = 18.0
SIMILAR_ROUTE_SPIKE_THRESHOLD = 18.0

# Context matching parameters
MATCH_WINDOW_DAYS = 14