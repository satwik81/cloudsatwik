import pandas as pd
df = pd.read_csv('employees_table.csv')
print("Original DataFrame:")
print(df)
df['Age_Doubled'] = df['Age'] * 2
filtered_df = df[df['Age'] > 25]
print("\nModified DataFrame:")
print(df)
print("\nFiltered DataFrame (Age > 25):")
print(filtered_df)
df.to_csv('modified_data.csv', index=False)
