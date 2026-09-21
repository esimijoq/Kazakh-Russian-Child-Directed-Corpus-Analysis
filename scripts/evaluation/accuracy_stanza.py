#!/usr/bin/env python3
"""Evaluate Stanza lemmas against manual annotations."""

# %%
#RUSSIAN
import pandas as pd

# Read Excel file
df = pd.read_excel("/content/sample_data/annotated_VS_stanza (2).xlsx")

# Compare Stanza output with manual annotation
df["Correct"] = df["Stanza"] == df["Annotated"]

# Number of tokens
n = len(df)

# Number of correct lemmas
correct = df["Correct"].sum()

# Accuracy
accuracy = correct / n * 100

print(f"Tokens: {n}")
print(f"Correct: {correct}")
print(f"Accuracy: {accuracy:.2f}%")

# %%
# Colab command: !pip install python-Levenshtein scikit-learn

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from Levenshtein import distance

# Read Excel file

df = pd.read_excel("/content/sample_data/annotated_VS_stanza (2).xlsx")

# Convert to strings (avoids problems with NaN values)

df["Annotated"] = df["Annotated"].astype(str)
df["Stanza"] = df["Stanza"].astype(str)

# Exact-match accuracy

df["Correct"] = df["Stanza"] == df["Annotated"]

n = len(df)
correct = df["Correct"].sum()
accuracy = correct / n * 100

# Average Levenshtein distance

avg_lev_dist = (
df.apply(lambda row: distance(row["Annotated"], row["Stanza"]), axis=1)
.mean()
)

# Precision, Recall, F1

precision = precision_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

recall = recall_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

f1 = f1_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

# Print results

print(f"Tokens: {n}")
print(f"Correct: {correct}")
print(f"Accuracy: {accuracy:.2f}%")
print(f"Average Levenshtein distance: {avg_lev_dist:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 score: {f1:.3f}")

# %%
#KAZAKH

import pandas as pd

# Read Excel file
df = pd.read_excel("/content/sample_data/kazakh.xlsx")

# Compare Stanza output with manual annotation
df["Correct"] = df["Stanza"] == df["Annotated"]

# Number of tokens
n = len(df)

# Number of correct lemmas
correct = df["Correct"].sum()

# Accuracy
accuracy = correct / n * 100

print(f"Tokens: {n}")
print(f"Correct: {correct}")
print(f"Accuracy: {accuracy:.2f}%")

# %%
# Colab command: !pip install python-Levenshtein scikit-learn

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from Levenshtein import distance

# Read Excel file

df = pd.read_excel("/content/sample_data/kazakh.xlsx")

# Convert to strings (avoids problems with NaN values)

df["Annotated"] = df["Annotated"].astype(str)
df["Stanza"] = df["Stanza"].astype(str)

# Exact-match accuracy

df["Correct"] = df["Stanza"] == df["Annotated"]

n = len(df)
correct = df["Correct"].sum()
accuracy = correct / n * 100

# Average Levenshtein distance

avg_lev_dist = (
df.apply(lambda row: distance(row["Annotated"], row["Stanza"]), axis=1)
.mean()
)

# Precision, Recall, F1

precision = precision_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

recall = recall_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

f1 = f1_score(
df["Annotated"],
df["Stanza"],
average="weighted",
zero_division=0
)

# Print results

print(f"Tokens: {n}")
print(f"Correct: {correct}")
print(f"Accuracy: {accuracy:.2f}%")
print(f"Average Levenshtein distance: {avg_lev_dist:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 score: {f1:.3f}")
