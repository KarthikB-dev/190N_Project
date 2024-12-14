import numpy as np
import pandas as pd
from itertools import combinations

DATA_LEN_PER_HOST_NUM = 200
PKS_PER_HOST = 1000
INPUT = "../data/output_aws_12_1_full.csv"
df = pd.read_csv(INPUT)

# Get all the unique labels
labels = df["label"].unique()

new_labels = []

for label in labels:
    lab_count = len(df[df["label"] == label])
    print("Label", label, "Count", lab_count)
    if  lab_count > 1000:
        new_labels.append(label)

labels = new_labels
print("Selected labels", labels)
dfs = []


sessionId = 0

def subset_labels(df, labels):
    global sessionId
    ndf = df[df["label"].isin(labels)]
    currdfs = []
    for lab in labels:
        currdfs.append(ndf[ndf["label"] == lab].sample(PKS_PER_HOST, replace=False))
    ndf = pd.concat(currdfs, ignore_index=True)
    sessionId += 1
    print("SESSION SELECTION DONE FOR #", sessionId,end="\r")
    ndf.loc[:, 'label'] = len(labels)
    ndf.loc[:, 'session'] = sessionId
    dfs.append(ndf)


# Generate all combinations of labels
for i in range(1, len(labels) + 1):
    # For all possible numbers of hosts
    print(f"Selecting {i} labels")
    for c in range(DATA_LEN_PER_HOST_NUM):
        # Randomly select i labels
        l = np.random.choice(labels, i, replace=False)
        subset_labels(df, l)

df = pd.concat(dfs, ignore_index=True)
OUTPUT = f"../data/output_aws_12_1_subset.csv"
df.to_csv(OUTPUT, index=False)