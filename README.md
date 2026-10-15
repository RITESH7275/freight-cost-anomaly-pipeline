# Freight Tiger - Freight Cost Anomaly & Context Engine

## Executive Summary
This project delivers an end-to-end data engineering pipeline that analyzes freight rate dynamics across major Indian logistics corridors. It processes raw daily shipment logs into weekly route aggregations, computes weighted unit economics (`cost_per_tonne_km`), evaluates rate spikes against dual baselines, and cross-references spikes against operational context notes to detect unexplained anomalies.

## Key Technical Features
- **Weighted Unit Economics**: Evaluates $\text{cost\_per\_tonne\_km} = \frac{\sum \text{freight\_cost\_inr}}{\sum (\text{quantity\_tonnes} \times \text{distance\_km})}$ to prevent volume skew.
- **Dual-Baseline Anomaly Detection**: Evaluates rate deviations against both historical route baselines and same-week similar route categories.
- **Contextual NLP Matching Engine**: Distinguishes justified surcharges (e.g., highway flooding, regional festivals) from unexplained spikes requiring human audit.
- **Production Architecture**: Designed using modular code patterns with decoupled components for configuration, data loading, analytics, and reasoning.

## Directory Structure
```text
.
├── data/                       # Input datasets and output CSV
│   ├── shipment_records.csv
│   ├── context_notes.csv
│   ├── sample_output_format_v2.csv
│   └── final_output.csv
├── src/                        # Source modules
│   ├── __init__.py
│   ├── config.py               # Settings, paths, and thresholds
│   ├── loader.py               # Ingestion, date parsing, and cleaning
│   ├── metrics.py              # Math calculations & baselines
│   └── matcher.py              # Context note reasoning engine
├── main.py                     # Entry point orchestrator
├── requirements.txt            # Dependency specification
└── README.md                   # Operational guide