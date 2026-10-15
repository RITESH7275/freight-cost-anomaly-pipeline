"""
Data loading and preprocessing module.
Includes robust handling for duplicate entries and missing (null) values.
"""

import pandas as pd
from src.config import SHIPMENTS_PATH, NOTES_PATH

def load_data():
    """Reads CSVs, removes duplicates, handles null values, and standardizes dates."""
    shipments = pd.read_csv(SHIPMENTS_PATH)
    notes = pd.read_csv(NOTES_PATH)

    # 1. Clean string whitespace
    string_cols = shipments.select_dtypes(include='object').columns
    shipments[string_cols] = shipments[string_cols].apply(lambda x: x.str.strip())

    # 2. De-duplication: Remove duplicate shipment records if any exist
    shipments = shipments.drop_duplicates(subset=['shipment_id'], keep='first')

    # 3. Null Value Management
    # Drop rows missing essential routing or financial parameters
    essential_cols = ['shipment_date', 'origin', 'destination', 'freight_cost_inr', 'quantity_tonnes', 'distance_km']
    shipments = shipments.dropna(subset=essential_cols)

    # Fill missing optional text columns if present
    shipments['material'] = shipments['material'].fillna('Unknown')
    shipments['transporter'] = shipments['transporter'].fillna('Unassigned')

    # 4. Standardize dates and assign route keys
    shipments['shipment_date'] = pd.to_datetime(shipments['shipment_date'])
    notes['date'] = pd.to_datetime(notes['date'])

    shipments['route'] = shipments['origin'] + '-' + shipments['destination']
    shipments['week_of'] = shipments['shipment_date'].dt.to_period('W-SUN').dt.start_time

    return shipments, notes