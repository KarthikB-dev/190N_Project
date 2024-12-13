import pandas as pd
import numpy as np
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

from tensorflow.keras.callbacks import ModelCheckpoint

# Select relevant features
label_column = "label"
features = ["protocol", "flags", "src_ip", "src_port", "dst_ip", "dst_port"]
categorical_columns = [label_column, "protocol", "flags", "src_ip", "dst_ip"]

if __name__ == "__main__":
    # Load CSV file
    csv_file = "../data_util/data/output.csv"  # Replace with your file path
    df = pd.read_csv(csv_file)
    
    # Encode categorical columns (e.g., `protocol`, `flags`) using LabelEncoder
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

    for i in range(10000):  # Group by a session identifier, e.g., 'src_ip'
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
    X_train, X_test, y_train, y_test = train_test_split(
        padded_sequences, labels, test_size=0.2, random_state=42
    )

    # Build an LSTM model
    model = Sequential(
        [
            LSTM(64, input_shape=(sequence_length, len(features))),
            Dense(32, activation="relu"),
            Dense(1),
        ]
    )
    checkpoint = ModelCheckpoint(
        filepath='checkpoints/model_epoch_{epoch:02d}.keras',  # Filepath pattern
        save_best_only=False,  # Save all models (set to True to save only the best model)
        save_weights_only=False,  # Save the entire model, not just weights
        verbose=1  # Print confirmation when saving
    )
    # model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.compile(optimizer="adam", loss="mse", metrics=["mse"])


    # Train the model
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=32, callbacks=[checkpoint])

    # Evaluate the model
    loss, MSE = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss}, Test MSE: {MSE}")

    model.save('nat_count_rnn.keras')
    ## Okay moment of truth
    # Predict on a new sequence
    test_data = df.sample(n=10000)
    new_sequence = test_data[features].values  # Example new sequence
    padded_sequence = pad_sequences([new_sequence], maxlen=sequence_length, padding="post")
    prediction = model.predict(padded_sequence)
    print(f"Predicted unique count: {prediction[0][0]:.2f}")

    ground_truth = len(test_data[label_column].unique())
    print(f"Ground truth unique count: {ground_truth}")