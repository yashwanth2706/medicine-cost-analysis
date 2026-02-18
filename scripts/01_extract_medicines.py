import pandas as pd
import re

df = pd.read_excel('Task_-_DC.xlsx', sheet_name='1yr - Mem', header=0)

def clean_med(name):
    name = str(name).strip().lower()
    name = name.strip('`').strip('.')
    name = re.sub(r'\s+', ' ', name).strip()
    return name

meds = set()
for col in ['start_medicines', 'Latest_medicines']:
    for val in df[col].dropna():
        for med in str(val).split(','):
            cleaned = clean_med(med)
            if cleaned and cleaned != 'nan':
                meds.add(cleaned)

result = pd.DataFrame({'medicine_name': sorted(meds)})
result.to_excel('medicine_list.xlsx', index=False)
print(f"Total: {len(meds)}")
