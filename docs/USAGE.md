# Usage Guide

## Running the Pipeline

### Step 1: Extract Medicine Names
```bash
python scripts/01_extract_medicines.py
```
**Output:** `data/processed/medicine_list.xlsx` (raw list)

### Step 2: Basic Normalization
```bash
python scripts/02_normalize_basic.py
```
**Output:** `data/processed/medicine_normalized_basic.xlsx`

### Step 3: Advanced Normalization
```bash
python scripts/03_normalize_advanced.py
```
**Output:** `data/processed/medicine_normalized.xlsx` (647 unique names)

### Step 4: Generate Final Analysis
```bash
python scripts/04_final_analysis.py
```
**Output:** `data/output/medicines_final.xlsx`

## Manual Steps

### Fill Prices
1. Open `data/output/medicines_final.xlsx`
2. Go to `medicine_prices` sheet
3. Fill column `C` (medicine_price) by searching Tata 1mg
4. Save file

### Add Formulas
In `medicines_expanded` sheet:

**Column F (price_difference)** - in first row of each client group:
```
=SUM(C2:C3) - SUM(E2:E3)
```
(Adjust range based on how many rows that client has)

**Column G (expense_difference)** - already shows Increase/Decrease/No Change

## Tips

- Use Google Sheets "Find & Replace" for batch cleaning: `1 mg` → `1mg`
- Sort medicine_prices by name for easier lookup
- Keep a separate tab in Sheets for price notes/sources