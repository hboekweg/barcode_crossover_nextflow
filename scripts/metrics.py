import pandas as pd

# df = pd.read_csv("read_classification_protocolA.csv")
df = pd.read_csv("read_classification_protocolB.csv")
# import pdb; pdb.set_trace()

#what is the percentage of reads that are classified as correct, crossover, ambiguous, and unmapped?
classification_counts = df["classification"].value_counts()
classification_percentages = classification_counts / len(df) * 100
print(classification_percentages)
