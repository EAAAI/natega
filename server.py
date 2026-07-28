from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import re
import os

app = Flask(__name__, static_folder='.')

# Arabic text normalization for better search
def normalize_arabic(text):
    """Normalize Arabic text for search matching"""
    if not isinstance(text, str):
        return ''
    # Remove tashkeel (diacritics)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]', '', text)
    # Normalize hamza forms
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'[ؤ]', 'و', text)
    text = re.sub(r'[ئ]', 'ي', text)
    # Normalize taa marbuta and haa
    text = text.replace('ة', 'ه')
    # Normalize alef maqsura and yaa
    text = text.replace('ى', 'ي')
    # Remove extra whitespace
    text = ' '.join(text.split())
    text = text.strip()
    return text


# Load data once into memory for fast search
print("⏳ جاري تحميل البيانات...")
DATA_PATH = os.path.join(os.path.dirname(__file__), 'results.csv')
df = pd.read_csv(DATA_PATH)
df['seating_no'] = df['seating_no'].astype(str)
df['arabic_name'] = df['arabic_name'].astype(str)
df['total_degree'] = df['total_degree'].astype(float)
df['percentage'] = df['percentage'].astype(float)
df['top_percent'] = df['top_percent'].astype(float)
df['rank'] = df['rank'].astype(int)
TOTAL_STUDENTS = len(df)

# Pre-compute normalized names for fast search
print("⏳ جاري تجهيز فهرس البحث بالاسم...")
df['name_normalized'] = df['arabic_name'].apply(normalize_arabic)

# Build a lookup dict for seat numbers (instant O(1) lookup)
seat_lookup = {}
for idx, row in df.iterrows():
    seat_lookup[row['seating_no']] = idx

print(f"✅ تم تحميل {TOTAL_STUDENTS:,} طالب بنجاح!")

# Convert name_normalized to numpy array for faster search
names_array = df['name_normalized'].values


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'seat')  # 'seat' or 'name'

    if not query:
        return jsonify({'results': [], 'total': 0})

    # Auto-detect: if query is all digits, search by seat number
    # Otherwise search by name regardless of what frontend sends
    if query.isdigit():
        search_type = 'seat'
    else:
        search_type = 'name'

    total_found = 0

    if search_type == 'seat':
        # Instant O(1) lookup for seat number
        idx = seat_lookup.get(query)
        if idx is not None:
            results = df.iloc[[idx]]
            total_found = 1
        else:
            results = df.iloc[0:0]  # empty
            total_found = 0
    else:
        # Name search - normalize query and match from START of name
        normalized_query = normalize_arabic(query)
        parts = normalized_query.split()
        
        if len(parts) < 2:
            return jsonify({'results': [], 'total': 0, 'error': 'يرجى إدخال اسمين على الأقل للبحث'})
        
        # Match from the beginning of the name
        # Also handle merged words like "علاءالدين" vs "علاء الدين"
        search_phrase = ' '.join(parts)
        search_nospace = ''.join(parts)
        
        mask = np.array([
            name.startswith(search_phrase) or name.replace(' ', '').startswith(search_nospace)
            for name in names_array
        ])
        
        matching_indices = np.where(mask)[0]
        total_found = len(matching_indices)
        
        # Limit to first 50 results
        results = df.iloc[matching_indices[:50]]

    records = []
    for _, row in results.iterrows():
        records.append({
            'seating_no': row['seating_no'],
            'name': row['arabic_name'].strip(),
            'total': row['total_degree'],
            'percentage': row['percentage'],
            'status': row['student_case_desc'].strip(),
            'rank': int(row['rank']),
            'top_percent': row['top_percent'],
            'total_students': TOTAL_STUDENTS
        })

    return jsonify({
        'results': records,
        'total': total_found
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Return overall statistics"""
    return jsonify({
        'total_students': TOTAL_STUDENTS,
        'passed': int(df[df['student_case_desc'] == 'ناجح دور أول'].shape[0]),
        'second_round': int(df[df['student_case_desc'] == 'دور ثان'].shape[0]),
        'failed': int(df[df['student_case_desc'].str.contains('راسب', na=False)].shape[0]),
        'absent': int(df[df['student_case_desc'].str.contains('غياب', na=False)].shape[0]),
        'highest': float(df['total_degree'].max()),
        'average': round(float(df[df['student_case_desc'] == 'ناجح دور أول']['total_degree'].mean()), 2)
    })


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
