import pandas as pd
import json

df = pd.read_excel('نتيجة_الثانوية_العامة_2025_كاملة_جميع_المحافظات.xlsx', nrows=5)
print(df.columns)
print(df.head())
