# Find closest passage for each passage
import os
from sys import exit
import pickle
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.join(os.getenv('HOME'), 'argument')
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PASSAGES = os.path.join(PROCESSED_DIR, "passages.csv")
EMBEDDINGS = os.path.join(PROCESSED_DIR, "embeddings.pkl")
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "closest_match.csv")

# Load csv with passages from preprocess_texts.py
# id,author,work,year,passage
if os.path.exists(PASSAGES):
    print("Loading saved passages...")
    passages = pd.read_csv(PASSAGES) 
else:
    print("Passages not found!")
    exit()

# <class 'numpy.ndarray'>
# shape = (n passages, 384)
if os.path.exists(EMBEDDINGS):
    print("Loading saved embeddings...")
    with open(EMBEDDINGS, "rb") as f:
        embeddings = pickle.load(f)
else:
    print("Embeddings not found!")
    exit()

# note that doing it full blast at once needs too much memory
#model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#similarity_matrix = model.similarity(embeddings, embeddings)

# TODO() - also return score?
def batched_cosine_sim(a, b, batch_size=128):
    # compute all the similarities and save only the index of the most similar
    results = []
    resulting_score = []
    for i in range(0, len(a), batch_size):
        print(f"{i} of {len(a)}")
        sims = cosine_similarity(
            a[i:i+batch_size], b
        )
        #print(sims.shape)
        # index of top score per row
        idx = np.argmax(sims, axis=1)
        #print(idx.shape)
        #results.append(sims)
        results.extend(idx)

        # value of top score per row
        scores = np.max(sims, axis=1)
        resulting_score.extend(scores)
    return results, resulting_score

# remake query and matching matrices for each author, to prevent self-matching
result_list = []
for author in passages["author"].unique():
    print(author)
    mask = (passages["author"] == author)
    author_passages = passages[mask]
    author_embeddings = embeddings[mask.values]

    selected_year = author_passages['year'].min()

    mask = ((passages["author"] != author) & (passages["year"] < selected_year))
    comparison_passages = passages[mask]
    comparison_embeddings = embeddings[mask.values]

    if author_embeddings.shape[0]>0 and comparison_embeddings.shape[0]>0:
        results, resulting_score = batched_cosine_sim(author_embeddings,comparison_embeddings)
        comparison_matches = comparison_passages.iloc[results].copy()

        comparison_matches["score"] = resulting_score

        # before combining, need to reindex
        to_combine = [author_passages,comparison_matches]
        dfs = [df.reset_index(drop=True) for df in to_combine]
        combined_results = pd.concat(dfs, axis=1, ignore_index=True)
        result_list.append(combined_results)

pd.concat(result_list, ignore_index=True).to_csv(OUTPUT_CSV)
print(f"Output saved to: {OUTPUT_CSV}")

exit()
