# Setup Guide

## Prerequisites

- Python 3.8+
- pip

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/medicine-cost-analysis.git
cd medicine-cost-analysis
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import pandas; import openpyxl; print('✓ All dependencies installed')"
```

## File Placement

Place your input Excel file at:
```
data/raw/Task_-_DC.xlsx
```

Expected sheet structure:
- Sheet name: `1yr - Mem`
- Columns: `clientid`, `start_medicines`, `Latest_medicines`, etc.