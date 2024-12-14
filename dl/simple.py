import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

# Example input data
data = [
    [[1.0], [1.0], [0.8], [1.0], [0.8]],
    [[0.6], [0.8], [1.0], [0.8], [0.6]],
    [[1.0], [1.0], [1.0], [0.8], [0.8]],
    # Add more sequences
]
labels = [2, 3, 2]  # Corresponding labels (number of unique values)

# Pad sequences to ensure uniform length
sequence_length = max(len(seq) for seq in data)
padded_data = pad_sequences(data, maxlen=sequence_length, padding='post', dtype='float32')

# Convert to numpy arrays
X = np.array(padded_data)
y = np.array(labels)

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build the RNN model
model = Sequential([
    SimpleRNN(32, input_shape=(sequence_length, 1), activation='relu'),
    Dense(16, activation='relu'),
    Dense(1)  # Single output for regression
])

# Compile the model
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train the model
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=20, batch_size=8)

# Evaluate the model
loss, mae = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}, Test MAE: {mae}")

# Predict on a new sequence
new_sequence = [[1.0], [0.8], [0.6], [1.0], [0.8]]  # Example new sequence
padded_sequence = pad_sequences([new_sequence], maxlen=sequence_length, padding='post', dtype='float32')
prediction = model.predict(padded_sequence)
print(f"Predicted unique count: {prediction[0][0]:.2f}")