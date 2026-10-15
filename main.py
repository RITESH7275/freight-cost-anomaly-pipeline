"""
Main entry point for Freight Tiger Anomaly Detection Pipeline.
Executes end-to-end data processing for ALL routes and weeks across the dataset.
"""

import logging
import sys
import pandas as pd
from src.config import (
    OUTPUT_PATH,
    HISTORICAL_SPIKE_THRESHOLD,
    SIMILAR_ROUTE_SPIKE_THRESHOLD,
    MATCH_WINDOW_DAYS
)
from src.loader import load_data
from src.metrics import calculate_weekly_metrics, compute_baselines
from src.matcher import find_explanation

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_pipeline():
    logging.info("Initializing Freight Tiger Anomaly Detection Pipeline...")

    try:
        # Load and preprocess raw data
        shipments, notes = load_data()
        logging.info("Datasets loaded successfully.")

        # Aggregate weekly metrics for all routes
        weekly = calculate_weekly_metrics(shipments)
        logging.info("Weekly unit economics and aggregations computed.")

        output_rows = []

        # Process all route-week combinations
        for (route, week_start), group in weekly.groupby(['route', 'week_of']):
            row = group.iloc[0]
            cost_val = round(row['cost_per_tonne_km'], 2)
            route_type = row['route_type']

            # Baseline comparisons
            vs_own_pct, vs_sim_pct = compute_baselines(
                weekly, route, week_start, route_type, row['cost_per_tonne_km'] # type: ignore
            )

            vs_own_str = f"{'+' if vs_own_pct >= 0 else ''}{vs_own_pct:.1f}% vs this route's past average"
            vs_sim_str = f"{'+' if vs_sim_pct >= 0 else ''}{vs_sim_pct:.1f}% vs similar-length routes this week"

            # Check threshold conditions
            is_spike = (vs_own_pct > HISTORICAL_SPIKE_THRESHOLD) or (vs_sim_pct > SIMILAR_ROUTE_SPIKE_THRESHOLD)

            matched_note, closest_irrelevant = None, None
            if is_spike:
                matched_note, closest_irrelevant = find_explanation(
                    route, week_start, notes, window_days=MATCH_WINDOW_DAYS # type: ignore
                )

            # Assign flagged state and reason
            if matched_note is not None:
                flagged = "No (justified)"
                matched_id = matched_note['note_id']
                reason = (
                    f"Matches note {matched_id} dated {matched_note['date'].strftime('%Y-%m-%d')}: "
                    f"{matched_note['note']}"
                )
            elif is_spike:
                flagged = "Yes"
                matched_id = ""
                if closest_irrelevant is not None:
                    c_id = closest_irrelevant['note_id']
                    c_date = closest_irrelevant['date'].strftime('%Y-%m-%d')
                    reason = (
                        f"The closest note ({c_id}, {c_date}) mentions {closest_irrelevant['note']} "
                        "-- it does not describe a reason for a cost rise on this route. "
                        "No genuine justification found; flagged for review."
                    )
                else:
                    reason = "No matching note found for this route or date range. Cost rise looks unexplained and worth a human review."
            else:
                flagged = "No"
                matched_id = ""
                reason = "Normal price variation within expected limits."

            output_rows.append({
                'route': route,
                'week_of': week_start.strftime('%Y-%m-%d'), # type: ignore
                'cost_per_tonne_km': cost_val,
                'vs_own_history': vs_own_str,
                'vs_similar_routes': vs_sim_str,
                'flagged': flagged,
                'matched_note_id': matched_id,
                'reason': reason
            })

        # Save output
        final_df = pd.DataFrame(output_rows)
        final_df.to_csv(OUTPUT_PATH, index=False)
        logging.info("Pipeline completed successfully. Exported %d rows to '%s'.", len(final_df), OUTPUT_PATH)

    except Exception as e:
        logging.error("Pipeline execution failed: %s", str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()