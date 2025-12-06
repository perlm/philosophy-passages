# Check embeddings for reasonableness
import os
from sys import exit
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from random import choice

BASE_DIR = os.path.join(os.getenv('HOME'), 'argument')
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PASSAGES = os.path.join(PROCESSED_DIR, "passages.csv")
EMBEDDINGS = os.path.join(PROCESSED_DIR, "embeddings.pkl")

# Load csv with passages from preprocess_texts.py
# id,author,work,year,passage
if os.path.exists(PASSAGES):
    print("Loading saved passages...")
    works = pd.read_csv(PASSAGES) 
else:
    print("Passages not found!")
    exit()

if os.path.exists(EMBEDDINGS):
    print("Loading saved embeddings...")
    with open(EMBEDDINGS, "rb") as f:
        embeddings = pickle.load(f)
else:
    print("Embeddings not found!")
    exit()


# Let's do some spot checking!
random_index = choice(list(works.index))
random_selection = works.iloc[random_index]
selected_author = random_selection['author']

#print(random_index)
print(random_selection)
#print(embeddings[random_index])
#print(selected_author)

query_embedding = embeddings[random_index].reshape(1, -1)
# reshape(1,-1) # shape goes from (N,) → (1, N).
#print(query_embedding)

# Find related passages
exclude_mask = ~(works["author"] == selected_author)
filtered_works = works[exclude_mask]
filtered_embeddings = [embeddings[i] for i in works[exclude_mask].index]

sims = cosine_similarity(query_embedding, filtered_embeddings)[0]
top_indices = sims.argsort()[::-1][:5]  # top 5 matches
top_values = sims[top_indices]

print("\nSelected passage:")
print(works.loc[random_index, "passage"])
print("\nTop related passages:")
for x in range(5):
    row = filtered_works.iloc[top_indices[x]]
    score = top_values[x]
    #row = filtered_works.iloc[idx]
    print(f"\n{row['author']} – {row['work']}")
    print(f"score={score}")
    print(row['passage'])

