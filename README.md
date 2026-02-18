# Medicine Cost Analysis

Automated tool for analyzing medicine cost changes across patient treatments.

## Features

- Medicine name normalization (handles spacing, units, variants)
- Patient-wise medicine tracking
- Cost difference calculation
- Automated Excel report generation with merged cells
- Clean data structure for price lookups

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
Place your raw Excel file in `data/raw/Task_-_DC.xlsx`

### 3. Run Scripts (in order)
```bash
# Extract unique medicine names
python scripts/01_extract_medicines.py

# Basic normalization (spacing, units)
python scripts/02_normalize_basic.py

# Advanced normalization (add missing units)
python scripts/03_normalize_advanced.py

# Generate final analysis sheet
python scripts/04_final_analysis.py
```

### 4. Output
Find your results in `data/output/medicines_final.xlsx`

## File Structure
```
medicines_final.xlsx
├── medicines_expanded    # One row per medicine per client
│   ├── clientid
│   ├── start_medicine
│   ├── start_medicine_price (fill from medicine_prices)
│   ├── latest_medicine
│   ├── latest_medicine_price (fill from medicine_prices)
│   ├── price_difference (merged per client - add formula)
│   └── expense_difference (merged per client - shows Increase/Decrease)
│
└── medicine_prices       # Master price lookup table
    ├── #
    ├── medicine_name (647 unique normalized names)
    └── medicine_price (₹) (fill from Tata 1mg)
```

## Workflow

1. **Extract** → Get all unique medicine names
2. **Normalize** → Clean spacing, standardize units, collapse duplicates
3. **Expand** → One row per medicine per patient
4. **Fill Prices** → Update `medicine_prices` sheet from Tata 1mg
5. **Auto-Calculate** → Use VLOOKUP to populate prices, add formulas for differences

## Data Normalization Rules

- Lowercase all names
- Remove extra spaces, backticks, trailing dots
- Standardize units: `1 mg` → `1mg`
- Smart unit addition: `amaryl 1` → `amaryl 1mg` (only if `amaryl 1mg` exists)
- Preserve dosage formats: `50/500`, `10/1000` etc.

## License

MIT

## Author

Your Name