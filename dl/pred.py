import pandas as pd
import numpy as np
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

from tensorflow.keras.callbacks import ModelCheckpoint
from tf import features, label_column, categorical_columns

# Load CSV file
csv_file = "../data_util/data/output_aws_12.csv"  # Replace with your file path
df = pd.read_csv(csv_file)

label_encoders = {col: LabelEncoder() for col in categorical_columns}
for col in categorical_columns:
    df[col] = label_encoders[col].fit_transform(df[col])

# Normalize numeric features
scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

print(df.head())

# Create sequences grouped by timestamp or a meaningful identifier (e.g., session-based)
# Assuming data is sorted by timestamp; otherwise, sort first
sequence_length = 10000  # Max length of each sequence
sequences = []
labels = []

for i in range(100):  # Group by a session identifier, e.g., 'src_ip'
    group = df.sample(n=10000)
    group_sequences = group[features].values
    group_labels = len(group[label_column].unique())

    sequences.append(group_sequences)
    labels.append(group_labels)

# print(len(sequences), len(labels))
# print(sequences[0], labels[0])

padded_sequences = pad_sequences(sequences, maxlen=sequence_length, padding="post")

# Convert labels to numpy array
labels = np.array(labels)

# Split into train and test sets
X_test, y_test = (padded_sequences, labels)

# Build an LSTM model
model = keras.models.load_model('nat_count_rnn.keras')

# Evaluate the model
loss, MSE = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}, Test MSE: {MSE}")

test_data = df.sample(n=10000)
new_sequence = test_data[features].values  # Example new sequence
padded_sequence = pad_sequences([new_sequence], maxlen=sequence_length, padding="post")
prediction = model.predict(padded_sequence)
print(f"Predicted unique count: {prediction[0][0]:.2f}")

ground_truth = len(test_data[label_column].unique())
print(f"Ground truth unique count: {ground_truth}")