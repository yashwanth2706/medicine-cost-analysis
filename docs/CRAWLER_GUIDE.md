# Tata 1mg Medicine Price Crawler Guide

Automatically fetch medicine prices from Tata 1mg and populate your analysis with real MRP data.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Understanding Results](#understanding-results)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Limitations](#limitations)

---

## Overview

The crawler automates the tedious process of manually searching 600+ medicines on Tata 1mg. It:

- ✅ Searches Tata 1mg for each medicine name
- ✅ Extracts **MRP prices** (ignores discounts/offers)
- ✅ Uses **fuzzy matching** to find closest product names
- ✅ **Color-codes results** for easy verification
- ✅ Auto-saves progress every 50 medicines
- ✅ Handles rate limits and retries automatically

### Time Estimate

- **698 medicines** × 2 seconds per search = **~23 minutes**
- Progress is saved incrementally (safe to interrupt)

---

## Installation

### Prerequisites

- Python 3.8+
- Internet connection
- `medicine_normalized.xlsx` (output from step 3)

### Install Dependencies

```bash
pip install -r requirements_crawler.txt
```

This installs:
- `pandas` - Excel file handling
- `openpyxl` - Excel formatting and colors
- `requests` - HTTP requests to Tata 1mg
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML parser backend

---

## Quick Start

### Basic Usage

```bash
cd scripts
python tata1mg_crawler_bs4.py
```

### Expected Output

```
============================================================
Tata 1mg Crawler (BeautifulSoup)
============================================================

📂 Loading medicine_normalized.xlsx...
🔍 Searching 647 medicines on Tata 1mg...

[1/647] amaryl 1mg
  ✓ EXACT: Amaryl 1mg Tablet 15's - ₹54.50

[2/647] metformin 500mg
  ~ CLOSE (87%): Glycomet 500mg Tablet 20's - ₹18.90

[3/647] januvia 100mg
  ✓ EXACT: Januvia 100mg Tablet 7's - ₹412.00

...

💾 Progress saved (50/647)

...

✅ Complete!
  🟢 Exact: 423
  🟠 Close: 184 (verify)
  🟡 Low match: 28
  ⚪ Not found: 12
```

---

## How It Works

### 1. Search Strategy

For each medicine, the crawler:

1. **Builds search URL**: `https://www.1mg.com/search/all?name=amaryl+1mg`
2. **Fetches HTML** with proper headers
3. **Parses product cards** using BeautifulSoup
4. **Extracts**:
   - Product name
   - MRP price (₹)
5. **Calculates similarity** between your name and found product
6. **Classifies match quality**

### 2. Fuzzy Matching

Uses `SequenceMatcher` to compare strings:

```python
Input:  "amaryl 1mg"
Found:  "Amaryl 1mg Tablet 15's"
Score:  0.92 (92% similar) → EXACT MATCH ✓
```

```python
Input:  "metformin 500mg"
Found:  "Glycomet 500mg Tablet"
Score:  0.78 (78% similar) → CLOSE MATCH (verify)
```

### 3. Price Extraction

- Looks for "MRP ₹XXX" patterns
- Ignores discounted prices
- Extracts numeric value only
- Example: `"MRP ₹123.45"` → `123.45`

### 4. Rate Limiting

- **2 seconds** between requests (respectful to server)
- **Exponential backoff** on rate limit (429) errors
- **3 retries** on timeout/failure

---

## Understanding Results

### Output File: `medicine_list_with_prices.xlsx`

| Column | Description |
|--------|-------------|
| `#` | Row number |
| `medicine_name` | Your original medicine name |
| `price (₹)` | *(Empty - not used)* |
| `found_product_name` | Product name found on Tata 1mg |
| `mrp_price` | MRP price in ₹ |
| `match_score` | Similarity (0.0 to 1.0) |
| `match_type` | exact / close / low_match / not_found |

### Color Coding

| Color | Match Type | Similarity | Action Required |
|-------|------------|------------|-----------------|
| 🟢 **Green** | Exact | ≥90% | ✅ Safe to use |
| 🟠 **Orange** | Close | 60-89% | ⚠️ **Verify manually** |
| 🟡 **Yellow** | Low/Not found | <60% | ❌ Manual search needed |

### Example Row

```
medicine_name:        amaryl 2mg
found_product_name:   Amaryl 2mg Tablet 15's
mrp_price:            84.50
match_score:          0.95
match_type:           exact
[Green highlight] ✓
```

---

## Advanced Usage

### Customize Input/Output Files

Edit at top of `tata1mg_crawler_bs4.py`:

```python
INPUT_FILE = '../data/processed/medicine_normalized.xlsx'
OUTPUT_FILE = '../data/output/medicine_prices_crawled.xlsx'
```

### Adjust Rate Limiting

If getting rate limited (429 errors), increase delay:

```python
time.sleep(5)  # Change from 2 to 5 seconds
```

### Change Similarity Thresholds

```python
if score >= 0.95:  # More strict (was 0.9)
    match_type = 'exact'
elif score >= 0.70:  # More strict (was 0.6)
    match_type = 'close'
```

### Resume Interrupted Crawl

The crawler auto-saves progress every 50 medicines. If interrupted:

1. Check `medicine_list_with_prices.xlsx`
2. See which row it stopped at (last filled `mrp_price`)
3. Edit script to skip completed rows:

```python
# Add after loading DataFrame
start_from = 150  # Skip first 150 already done
df = df.iloc[start_from:]
```

---

## Troubleshooting

### Problem: "Not found" for common medicines

**Cause:** Tata 1mg uses different product names

**Solution:**
1. Manually search the medicine on Tata 1mg
2. Copy exact product name from search results
3. Update your `medicine_normalized.xlsx` with exact Tata 1mg name
4. Re-run crawler for that medicine

**Example:**
```
Your name:    "metformin sr 500mg"
Tata 1mg has: "Glycomet SR 500mg"
→ Update your sheet to "glycomet sr 500mg"
```

---

### Problem: Too many 429 errors (Rate Limited)

**Cause:** Requests too frequent

**Solution:**
```python
# In script, change:
time.sleep(2)  # to
time.sleep(5)  # or even 10
```

Wait 1-2 hours before retrying if you hit rate limits.

---

### Problem: Connection timeouts

**Cause:** Network issues or slow connection

**Solution:**
1. Check internet connection
2. Increase timeout in script:
```python
response = requests.get(url, timeout=30)  # from 15
```
3. The script auto-retries 3 times

---

### Problem: Prices seem wrong or outdated

**Cause:** Tata 1mg updated their prices

**Solution:**
- Medicine prices change frequently
- Always verify critical/high-value medicines manually
- Re-run crawler periodically for updated prices

---

### Problem: BeautifulSoup not finding products

**Cause:** Tata 1mg changed their HTML structure

**Solution:**
1. Try the basic crawler as fallback:
```bash
python tata1mg_crawler.py
```
2. Or manually inspect Tata 1mg HTML and update selectors in script

---

## Best Practices

### ✅ Do's

- ✅ **Always verify orange cells** before using prices
- ✅ Run during off-peak hours (less likely to hit rate limits)
- ✅ Keep the 2-second delay (be respectful to server)
- ✅ Save progress files regularly
- ✅ Double-check high-value medicines manually
- ✅ Re-run crawler every few months for updated prices

### ❌ Don'ts

- ❌ Don't reduce delay below 2 seconds
- ❌ Don't run multiple instances simultaneously
- ❌ Don't use for commercial/bulk scraping
- ❌ Don't trust low-similarity matches blindly
- ❌ Don't skip manual verification of orange cells

---

## Verification Workflow

After crawler finishes:

### Step 1: Review Statistics

Check the final summary:
```
🟢 Exact: 423    → These are safe
🟠 Close: 184    → VERIFY ALL OF THESE
🟡 Low: 28       → Manual search needed
⚪ Missing: 12   → Manual search needed
```

### Step 2: Verify Orange Cells

1. Open `medicine_list_with_prices.xlsx`
2. Sort by `match_type` = "close"
3. For each orange row:
   - Check `found_product_name` vs `medicine_name`
   - Does the product match? (same medicine, same strength?)
   - If yes → keep the price
   - If no → manually search on Tata 1mg

### Step 3: Handle Yellow/Missing

1. Sort by `match_type` = "not_found" or "low_match"
2. Manually search each on Tata 1mg
3. Fill in correct MRP price

### Step 4: Spot Check Green Cells

Randomly verify 10-20 green cells to ensure accuracy.

---

## Integration with Main Pipeline

### Full Workflow with Crawler

```bash
# Step 1: Normalize medicines
python scripts/01_extract_medicines.py
python scripts/02_normalize_basic.py
python scripts/03_normalize_advanced.py

# Step 2: Crawl prices (~23 minutes)
cd scripts
python tata1mg_crawler_bs4.py
cd ..

# Step 3: Manual verification
# → Open medicine_list_with_prices.xlsx
# → Verify all orange cells
# → Fill yellow/missing cells

# Step 4: Copy prices to final sheet
# → Copy mrp_price column
# → Paste into medicine_prices sheet (Column C)

# Step 5: Generate final analysis
python scripts/04_final_analysis.py
```

---

## Limitations

### What the Crawler Can't Do

- ❌ **Cannot guarantee 100% accuracy** - Always verify
- ❌ **Cannot handle very generic names** - "insulin" returns many products
- ❌ **Cannot distinguish pack sizes** - May return 10's pack when you need 30's
- ❌ **Cannot access member-only prices** - Only shows public MRP
- ❌ **Cannot auto-update** - Prices need manual re-crawl

### When to Search Manually

- Complex combination medicines
- Very new medicines (just launched)
- Rare/specialty medications
- When brand vs generic matters
- When pack size is critical (10's vs 30's vs 100's)

---

## Legal & Ethical Considerations

### ✅ Allowed Use

- Personal medication cost analysis
- Research purposes
- One-time price data collection
- Comparative studies

### ❌ Prohibited Use

- Commercial reselling of data
- Automated/continuous monitoring
- Creating competing price databases
- Violating Tata 1mg Terms of Service

### Rate Limiting Ethics

This crawler is designed to be **respectful**:
- 2-second delays between requests
- Maximum 1800 requests/hour
- Proper User-Agent headers
- Exponential backoff on errors

**Do not modify these safeguards.**

---

## Performance Tips

### Speed vs Accuracy Trade-off

```python
# Faster (less accurate):
time.sleep(1)  # 1 second delay
retries=2      # 2 retries only

# Slower (more accurate):
time.sleep(5)  # 5 second delay
retries=5      # 5 retries
```

Recommended: **Stick with defaults** (2s delay, 3 retries)

### Parallel Processing

**Not recommended** - Will get you IP-banned. Run sequentially only.

---

## Sample Output Analysis

After a full run on 647 medicines:

```
Results Breakdown:
├── 423 Exact matches (65%)   → Use directly
├── 184 Close matches (28%)   → Verify manually
├── 28 Low matches (4%)       → Manual search
└── 12 Not found (2%)         → Manual search

Time taken: 22 minutes 14 seconds
```

**Action Items:**
- ✅ 423 medicines ready to use
- ⚠️ 184 need verification (~30-60 min manual work)
- ❌ 40 need manual search (~1-2 hours)

**Total manual effort:** 1.5 - 2.5 hours

vs.

**Manual searching all 647:** 10-15 hours

**Time saved:** ~85%

---

## Support

### Issues?

1. Check [Troubleshooting](#troubleshooting) section
2. Verify internet connection
3. Check Tata 1mg is accessible
4. Try basic crawler (`tata1mg_crawler.py`) as fallback

### Contributing

Found a bug or improvement?
- Update the script
- Test thoroughly
- Document changes
- Commit to repo

---

## Version History

- **v1.0** - Initial release with basic regex crawler
- **v2.0** - BeautifulSoup version with better parsing
- **v2.1** - Added color coding and progress saving
- **v2.2** - Improved fuzzy matching thresholds

---

## Appendix: Match Score Examples

| Your Name | Found Product | Score | Type |
|-----------|---------------|-------|------|
| amaryl 1mg | Amaryl 1mg Tablet 15's | 0.95 | 🟢 Exact |
| metformin 500 | Glycomet 500mg SR | 0.82 | 🟠 Close |
| janumet 50/1000 | Janumet 50/1000mg Tab | 0.91 | 🟢 Exact |
| some random text | Paracetamol 500mg | 0.12 | 🟡 Low |
| xyz medicine | *(not found)* | 0.00 | ⚪ Missing |

---

**Happy Crawling! 🕷️**