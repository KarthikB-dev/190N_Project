import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

df = pd.read_csv('100s_labeled.csv')

features = ['timestamp', 'src_port', 'dst_port', 'ttl', 'tos', 'data_length']

for feature in features:
    df[feature] = pd.to_numeric(df[feature], errors='coerce')

ip_counts = df['src_ip'].value_counts()

ips_to_keep = ip_counts[ip_counts > 1].index
df_filtered = df[df['src_ip'].isin(ips_to_keep)]

df_filtered['label_encoded'], _ = pd.factorize(df_filtered['src_ip'])

class_counts = df_filtered['label_encoded'].value_counts()
sufficient_classes = class_counts[class_counts > 1].index
df_filtered = df_filtered[df_filtered['label_encoded'].isin(sufficient_classes)]

X = df_filtered[features]
y = df_filtered['label_encoded']

test_size = 0.2

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=test_size, 
    stratify=y, 
    random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = XGBClassifier(
    n_estimators=100, 
    learning_rate=0.1, 
    random_state=42,
    use_label_encoder=False,
    eval_metric='mlogloss'
)
model.fit(X_train_scaled, y_train)

scaler = StandardScaler()

accuracy_list = []

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for train_idx, test_idx in cv.split(X, y):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    accuracy_list.append(accuracy_score(y_test, y_pred))

print(f"Manual Cross-Validation Accuracy Scores: {accuracy_list}")
print(f"Mean Accuracy: {np.mean(accuracy_list):.2f} ± {np.std(accuracy_list):.2f}")

y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))

unique_mapping = dict(zip(df_filtered['src_ip'], df_filtered['label_encoded']))
print("\nUnique Source IPs and Encoded Labels:")
for host, encoded in list(unique_mapping.items())[:20]:  # Limit to first 20
    print(f"{host}: {encoded}")

print("\nTotal unique IPs:", len(unique_mapping))
print("Original dataset size:", len(df))
print("Filtered dataset size:", len(df_filtered))

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
