import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Veri Seti (100 Simülasyonluk Refined Data)
data = {
    'Spymaster': ['EXPERT', 'EXPERT', 'EXPERT', 'EXPERT', 'EXPERT',
                  'GOOD', 'GOOD', 'GOOD', 'GOOD', 'GOOD',
                  'MID', 'MID', 'MID', 'MID', 'MID',
                  'BAD', 'BAD', 'BAD', 'BAD', 'BAD',
                  'TERRIBLE', 'TERRIBLE', 'TERRIBLE', 'TERRIBLE', 'TERRIBLE'],
    'Guesser': ['EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE',
                'EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE',
                'EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE',
                'EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE',
                'EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE'],
    'Success_Rate': [66.50, 56.00, 38.50, 39.00, 41.00,
                     66.00, 54.50, 41.00, 43.00, 36.00,
                     62.00, 49.50, 38.00, 40.00, 41.00,
                     60.50, 46.00, 40.50, 40.50, 43.00,
                     53.50, 40.50, 40.50, 42.00, 39.00],
    'Avg_Score': [1.02, 0.75, 0.23, 0.27, 0.28,
                  0.97, 0.64, 0.33, 0.30, 0.15,
                  0.85, 0.55, 0.16, 0.21, 0.23,
                  0.80, 0.43, 0.24, 0.26, 0.32,
                  0.52, 0.24, 0.20, 0.14, 0.20],
    'Fail_Blue': [10.00, 18.50, 27.00, 25.50, 27.00,
                  13.50, 21.50, 23.50, 27.00, 28.50,
                  14.00, 22.50, 29.00, 30.50, 27.50,
                  18.00, 25.00, 29.00, 29.00, 25.50,
                  26.00, 26.50, 29.00, 34.50, 27.50],
    'Lose_Black': [1.02, 0.00, 4.08, 4.59, 2.04,
                   0.00, 1.53, 2.55, 3.06, 5.61,
                   1.02, 2.04, 4.08, 3.06, 4.08,
                   0.51, 2.55, 3.06, 2.55, 2.55,
                   1.02, 4.08, 1.53, 1.53, 5.61]
}

df = pd.DataFrame(data)

# Profil sıralaması
order = ['EXPERT', 'GOOD', 'MID', 'BAD', 'TERRIBLE']

# 1. HEATMAP (Success Rate)
pivot_success = df.pivot(index="Spymaster", columns="Guesser", values="Success_Rate")
pivot_success = pivot_success.reindex(index=order, columns=order)

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_success, annot=True, fmt=".1f", cmap="RdYlGn", linewidths=.5)
plt.title('Success Rate Heatmap (100 Simulations)', fontsize=16)
plt.show()

# 2. GROUPED BAR CHART (Average Score Comparison)
plt.figure(figsize=(12, 6))
sns.barplot(x="Spymaster", y="Avg_Score", hue="Guesser", data=df, order=order, hue_order=order, palette="viridis")
plt.title('Average Score by Spymaster and Guesser Interaction', fontsize=16)
plt.ylabel('Average Score')
plt.legend(title='Guesser Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 3. STACKED BAR CHART (Risk analizi: Fail vs Lose)
# Veriyi stacked bar formatına uyarlama kısmı
df['Natural_Neutral'] = 100 - (df['Success_Rate'] + df['Fail_Blue'] + df['Lose_Black']) # Kalanı hesapla
risk_data = df[['Spymaster', 'Guesser', 'Fail_Blue', 'Lose_Black']].copy()
risk_data['Pair'] = risk_data['Spymaster'] + " - " + risk_data['Guesser']

selected_pairs = [
    'EXPERT - EXPERT',
    'GOOD - EXPERT',
    'GOOD - GOOD',
    'MID - MID',
    'BAD - BAD',
    'TERRIBLE - TERRIBLE',
    'EXPERT - TERRIBLE'
]

filtered_risk = risk_data[risk_data['Pair'].isin(selected_pairs)].set_index('Pair')

# Sıralamayı listedeki sıraya göre yapma kısmı
filtered_risk = filtered_risk.reindex(selected_pairs)

filtered_risk[['Fail_Blue', 'Lose_Black']].plot(kind='bar', stacked=True, color=['#3498db', '#2c3e50'], figsize=(10, 6))
plt.title('Risk Analysis: Fail (Blue) vs Catastrophe (Black) Rates', fontsize=16)
plt.ylabel('Percentage (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()