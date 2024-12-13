import pandas as pd
from itertools import combinations


INPUT = "../data/output.csv"
df = pd.read_csv(INPUT)

# Get all the unique labels
labels = df["label"].unique()

new_labels = []

for label in labels:
    if len(df[df["label"] == label]) > 500:
        new_labels.append(label)

labels = new_labels
print("Selected labels", labels)
dfs = []


sessionId = 0

def subset_labels(df, labels):
    global sessionId
    ndf = df[df["label"].isin(labels)].copy()
    sessionId += 1
    if len(ndf) > 1000:
        print("Selected session", sessionId)
        ndf.loc[:, 'label'] = len(labels)
        ndf.loc[:, 'session'] = sessionId
        dfs.append(ndf)


# Generate all combinations of labels
for i in range(1, len(labels) + 1):

    for c in combinations(labels, i):
        subset_labels(df, c)

df = pd.concat(dfs, ignore_index=True)
OUTPUT = f"../data/output_subset.csv"
df.to_csv(OUTPUT, index=False)