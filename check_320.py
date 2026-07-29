import pandas as pd
df = pd.read_excel('نتيجة_الثانوية_العامة_2025_كاملة_جميع_المحافظات.xlsx')
df['total_degree'] = pd.to_numeric(df['total_degree'], errors='coerce').fillna(0)
over_320 = len(df[df['total_degree'] > 320])
print(f"Students with score > 320: {over_320}")
print(f"Max score: {df['total_degree'].max()}")
