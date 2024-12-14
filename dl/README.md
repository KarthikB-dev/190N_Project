# The deep learning tools
This directory contains the deep learning tools for the project. The tools are written in Python and are used to train and evaluate the machine learning models. All the scripts uses `tensorflow` and `keras` as the backend, it also requires `numpy` and `pandas` to run.

## Tools
- `simple.py` is a AI generated example to show case the basic principle of our RNN model. It becomes handy when we are explaining the model to each other.
- `tf.py` is the `tensorflow` implementation of the RNN model, it is the first version of the model.
  - It takes in a `.csv` file produced by `label.py` and produces a model that can be used to predict the labels of the WAN traffic.
  - It uses random splitting to generate capture sessions with different hosts.
  - Input `.csv` file is hardcoded in the script, please change it according to your needs.
- `rnn_subset.py` is similar to `tf.py` but uses the subsets produced by `subset.py` instead of the full dataset.
  - It preserves the time sequence of the data, and uses the same model as `tf.py`.
- `pred.py` is the script that does the prediction on validation data, it takes in a `.csv` file produced by `label.py` and a model produced by `tf.py` or `rnn_subset.py` and produces the prediction.
  - It uses the same model as `tf.py` or `rnn_subset.py`.