"""
Unit economics and baseline calculation engine.
Calculates weighted cost_per_tonne_km and compares route performance against baselines.
"""

import pandas as pd

def calculate_weekly_metrics(shipments: pd.DataFrame) -> pd.DataFrame:
    """Calculates weighted unit cost (total freight cost / total tonne-km) grouped by week."""
    # Filter out invalid or zero quantity/distance entries
    valid_shipments = shipments[(shipments['quantity_tonnes'] > 0) & (shipments['distance_km'] > 0)].copy()

    # Pre-calculate tonne-km for each individual shipment
    valid_shipments['tonne_km'] = valid_shipments['quantity_tonnes'] * valid_shipments['distance_km']

    # Group by route and week, summing total cost and total tonne-km
    weekly_df = valid_shipments.groupby(['route', 'route_type', 'week_of']).agg(
        total_cost=('freight_cost_inr', 'sum'),
        total_tonne_km=('tonne_km', 'sum')
    ).reset_index()

    # Calculate exact weighted rate
    weekly_df['cost_per_tonne_km'] = weekly_df['total_cost'] / weekly_df['total_tonne_km']

    return weekly_df

def compute_baselines(weekly_df: pd.DataFrame, route: str, week_start: pd.Timestamp, route_type: str, current_cost: float):
    """
    Computes percentage comparisons across all historical weeks and similar routes:
    1. vs_own_history: Compares current week against prior weeks for this route.
    2. vs_similar_routes: Compares current week against other routes of the same type.
    """
    # Historical average for this route prior to current week
    past_records = weekly_df[(weekly_df['route'] == route) & (weekly_df['week_of'] < week_start)]
    if not past_records.empty:
        hist_avg = past_records['cost_per_tonne_km'].mean()
    else:
        hist_avg = weekly_df[weekly_df['route'] == route]['cost_per_tonne_km'].mean()

    vs_own_pct = ((current_cost - hist_avg) / hist_avg) * 100.0 if hist_avg > 0 else 0.0

    # Similar route average during the same week (excluding current route)
    similar_records = weekly_df[
        (weekly_df['route_type'] == route_type) & 
        (weekly_df['week_of'] == week_start) & 
        (weekly_df['route'] != route)
    ]
    if not similar_records.empty:
        similar_avg = similar_records['cost_per_tonne_km'].mean()
    else:
        similar_records = weekly_df[(weekly_df['route_type'] == route_type) & (weekly_df['week_of'] == week_start)]
        similar_avg = similar_records['cost_per_tonne_km'].mean()

    vs_sim_pct = ((current_cost - similar_avg) / similar_avg) * 100.0 if similar_avg > 0 else 0.0

    return vs_own_pct, vs_sim_pct