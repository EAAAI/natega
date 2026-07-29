import pandas as pd
import numpy as np
import json
import re
import os
import math

def normalize_arabic(text):
    if not isinstance(text, str): return ''
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'[ؤ]', 'و', text)
    text = re.sub(r'[ئ]', 'ي', text)
    text = text.replace('ة', 'ه')
    text = text.replace('ى', 'ي')
    return ' '.join(text.split()).strip()

print("Loading excel...")
df = pd.read_excel('نتيجة_الثانوية_العامة_2025_كاملة_جميع_المحافظات.xlsx')
print(f"Loaded {len(df)} rows.")

print("Calculating fields...")
# Ensure correct types
df['total_degree'] = pd.to_numeric(df['total_degree'], errors='coerce').fillna(0)

# User explicitly requested to delete scores over 320 and treat the file as out of 320
df = df[df['total_degree'] <= 320]
df['percentage'] = (df['total_degree'] / 320.0 * 100).round(2)

# Sort by total_degree descending to calculate rank
df = df.sort_values(by='total_degree', ascending=False).reset_index(drop=True)
df['rank'] = df.index + 1
total_students = len(df)
df['top_percent'] = ((df['rank'] / total_students) * 100).round(2)

# Case ID: 1 for passed (>= 50%), 3 for failed (< 50%)
df['case_id'] = np.where(df['percentage'] >= 50, 1, 3)

# Add normalized name
print("Normalizing names...")
df['arabic_name'] = df['arabic_name'].fillna('').astype(str)
df['normalized_name'] = df['arabic_name'].apply(normalize_arabic)
df['seating_no'] = df['seating_no'].astype(str)

print("Preparing chunks...")
# Convert to list of lists
# Format: [seat(0), name(1), norm_name(2), total(3), case(4), percent(5), rank(6), top_percent(7)]
records = []
for row in df.itertuples():
    records.append([
        row.seating_no,
        row.arabic_name,
        row.normalized_name,
        row.total_degree,
        int(row.case_id),
        row.percentage,
        int(row.rank),
        row.top_percent
    ])

# Sort back by seating_no to make chunks sequential
records.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

out_dir = 'json_data_2025'
os.makedirs(out_dir, exist_ok=True)

# Split into 7 chunks (0 to 6)
num_chunks = 7
chunk_size = math.ceil(len(records) / num_chunks)

for i in range(num_chunks):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(records))
    chunk_data = records[start:end]
    
    file_path = os.path.join(out_dir, f'data_{i}.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunk_data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Saved {file_path} with {len(chunk_data)} records.")

print("Calculating distribution for 2025...")
# Calculate bins: <50, 50-60, 60-70, 70-80, 80-90, 90-95, >95
bins = [0]*7
for r in records:
    pct = r[5]
    if pct >= 95: bins[6] += 1
    elif pct >= 90: bins[5] += 1
    elif pct >= 80: bins[4] += 1
    elif pct >= 70: bins[3] += 1
    elif pct >= 60: bins[2] += 1
    elif pct >= 50: bins[1] += 1
    else: bins[0] += 1

passed = sum(1 for r in records if r[4] == 1)
print(f"2025 Distribution Bins: {bins}")
print(f"2025 Success Rate: {passed / total_students * 100:.2f}%")
print("Done.")
