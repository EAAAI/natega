import pandas as pd
df = pd.read_excel('نتيجة_الثانوية_العامة_2025_كاملة_جميع_المحافظات.xlsx')
print(f"Max total_degree: {df['total_degree'].max()}")
print(f"Total rows: {len(df)}")
