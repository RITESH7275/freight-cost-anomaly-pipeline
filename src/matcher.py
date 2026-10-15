"""
Contextual reasoning engine.
Matches cost spikes against operational notes to explain rate anomalies.
"""

from typing import Tuple, Optional
import pandas as pd

def find_explanation(
    route: str, 
    week_start: pd.Timestamp, 
    notes: pd.DataFrame, 
    window_days: int = 14
) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
    """
    Cross-references rate spikes with context notes within a given time window.
    
    Returns:
        Tuple containing (matched_note, closest_irrelevant_note)
    """
    matched_note = None
    closest_irrelevant = None

    for _, note in notes.iterrows():
        applies_to = note['applies_to']
        note_date = note['date']
        days_diff = abs((week_start - note_date).days)

        route_matches = (applies_to == 'All Routes') or (applies_to == route)
        if route_matches and days_diff <= window_days:
            note_text = note['note'].lower()
            if any(k in note_text for k in ['flood', 'surcharge', 'pushed up', 'detour', 'disrupted']):
                matched_note = note
                break
            else:
                closest_irrelevant = note

    return matched_note, closest_irrelevant