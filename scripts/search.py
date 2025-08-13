import os
from sys import exit
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.join(os.getenv('HOME'), 'argument')
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
INPUT_PASSAGE = os.path.join(PROCESSED_DIR, "passages.csv")
OUTPUT_EMBED = os.path.join(PROCESSED_DIR, "embeddings.pkl")

# --- Step 1: Load CSV ---
df = pd.read_csv(INPUT_PASSAGE)  # from Step 2 output

# --- Load embeddings if they exist ---
if os.path.exists(OUTPUT_EMBED):
    print("Loading saved embeddings...")
    with open(OUTPUT_EMBED, "rb") as f:
        embeddings = pickle.load(f)
else:
    print("Embeddings not found!")
    exit()

# --- Work + passage selection ---
works = sorted(df[["author", "work"]].drop_duplicates().values.tolist())
for i, (author, work) in enumerate(works):
    print(f"{i}: {author} – {work}")

work_idx = int(input("Select a work by number: "))
selected_author, selected_work = works[work_idx]

passages = df[(df["author"] == selected_author) & (df["work"] == selected_work)]
start_idx = passages.index.min()
end_idx = passages.index.max()
print(f"Passage index range for this work: {start_idx}–{end_idx}")

passage_idx = int(input("Select a passage index: "))
if passage_idx < start_idx or passage_idx > end_idx:
    raise ValueError("Invalid passage index.")

query_embedding = embeddings[passage_idx].reshape(1, -1)

# --- Step 4: Find related passages (excluding same work) ---
exclude_mask = ~((df["author"] == selected_author) & (df["work"] == selected_work))
filtered_embeddings = [embeddings[i] for i in df[exclude_mask].index]
filtered_df = df[exclude_mask]

sims = cosine_similarity(query_embedding, filtered_embeddings)[0]
top_indices = sims.argsort()[::-1][:5]  # top 5 matches


print("\nSelected passage:")
print(df.loc[passage_idx, "passage"])
print("\nTop related passages:")
for idx in top_indices:
    row = filtered_df.iloc[idx]
    print(f"\n{row['author']} – {row['work']}")
    print(row['passage'])


