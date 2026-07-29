import json
import glob

bins = [0] * 7
passed = 0
total = 0

for file in glob.glob('json_data/data_*.json'):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for row in data:
            total += 1
            case_id = row[4]
            percentage = row[5]
            if case_id == 1:
                passed += 1
            if percentage >= 95: bins[6] += 1
            elif percentage >= 90: bins[5] += 1
            elif percentage >= 80: bins[4] += 1
            elif percentage >= 70: bins[3] += 1
            elif percentage >= 60: bins[2] += 1
            elif percentage >= 50: bins[1] += 1
            else: bins[0] += 1

print(f"2026 Bins: {bins}")
print(f"2026 Success Rate: {(passed / total) * 100:.2f}%")
