import json
import glob
import os

def process_dir(d):
    total = 0
    passed = 0
    second = 0
    failed = 0
    absent = 0
    score_sum = 0
    bins = [0]*7
    
    files = glob.glob(os.path.join(d, 'data_*.json'))
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            for row in data:
                total += 1
                score_sum += row[3]
                case = row[4]
                pct = row[5]
                
                if case == 1: passed += 1
                elif case == 2: second += 1
                elif case == 3: failed += 1
                elif case == 4: absent += 1
                
                if pct >= 95: bins[6] += 1
                elif pct >= 90: bins[5] += 1
                elif pct >= 80: bins[4] += 1
                elif pct >= 70: bins[3] += 1
                elif pct >= 60: bins[2] += 1
                elif pct >= 50: bins[1] += 1
                else: bins[0] += 1
                
    return {
        'total_students': total,
        'passed': passed,
        'second_round': second,
        'failed': failed,
        'absent': absent,
        'total_score_sum': score_sum,
        'distributionBins': bins
    }

print('2026:', process_dir('json_data'))
print('2025:', process_dir('json_data_2025'))
