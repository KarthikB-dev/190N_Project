import pandas as pd


INPUT = "../data/output.csv"
df = pd.read_csv(INPUT)

# Get all the unique labels
labels = df["label"].unique()
print(labels)


def subset_labels(df, labels):
    ndf = df[df["label"].isin(labels)]
    OUTPUT = f"../data/output_subset_{len(labels)}_{",".join(list(labels))}.csv"
    ndf.to_csv(OUTPUT, index=False)

# Generate all combinations of labels
for i in range(1, len(labels)+1):
    from itertools import combinations
    for c in combinations(labels, i):
        subset_labels(df, c)