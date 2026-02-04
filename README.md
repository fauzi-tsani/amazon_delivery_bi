# Amazon Delivery BI – ETL, Data Warehouse, Diagrams, Dashboard

This project builds a simple **Data Warehouse + BI Dashboard** from `amazon_delivery.csv`.

## Project Structure

```
.
├─ amazon_delivery.csv
├─ etl_pipeline.py
├─ generate_erd.py
├─ star_schema.py
├─ bus_matrix.py
├─ interactive_dashboard.py
├─ take_screenshots.py
├─ requirements.txt
├─ warehouse_data/                 # created by ETL
└─ diagrams/                       # created by diagram scripts
```

## Requirements

- Python 3
- pip

## Install Dependencies

```bash
pip install -r requirements.txt

# Dashboard extras
pip install dash dash-bootstrap-components plotly statsmodels

# (Optional) Screenshot tool
pip install playwright
playwright install chromium
```

## 1) Run ETL (Build Star Schema Tables)

```bash
python3 etl_pipeline.py
```

Outputs (created in `warehouse_data/`):
- `Dim_Agent.csv`
- `Dim_Time.csv`
- `Dim_Location.csv`
- `Dim_Weather.csv`
- `Dim_Vehicle.csv`
- `Dim_Category.csv`
- `Fact_Delivery.csv`

## 2) Generate Diagrams

```bash
python3 generate_erd.py
python3 star_schema.py
python3 bus_matrix.py
```

Outputs (created in `diagrams/`):
- `erd_diagram.png` (+ `erd_legend.txt`)
- `star_schema.png` (+ `star_schema_summary.txt`)
- `enterprise_bus_matrix.png`

## 3) Run Interactive Dashboard (Plotly Dash)

```bash
python3 interactive_dashboard.py
```

Open:
- http://127.0.0.1:8050

### Notes
- Filters supported: **Date range**, **Area**, **Category**, **Weather**
- KPI “Total Distance” uses `Distance_KM` computed from store/drop coordinates (Haversine).

## 4) Take Screenshots of All Pages

Make sure dashboard is running, then:

```bash
python3 take_screenshots.py
```

Outputs:
- `screenshot_1_executive_summary.png`
- `screenshot_2_delivery_performance.png`
- `screenshot_3_agent_performance.png`

## Troubleshooting

### `ModuleNotFoundError: No module named 'dash'`
```bash
pip install dash dash-bootstrap-components
```

### `ModuleNotFoundError: No module named 'statsmodels'`
Plotly trendlines require statsmodels:
```bash
pip install statsmodels
```

### Dashboard filter option error: `TypeError: '<' not supported between instances of 'float' and 'str'`
This happens when a column has NaN mixed with strings. The dashboard code now filters NaN and converts values to strings for sorting.

---

If you want the dashboard to load from the **warehouse_data fact/dim tables** (instead of directly from `amazon_delivery.csv`), tell me and I’ll switch the dashboard data source to the star schema output.
