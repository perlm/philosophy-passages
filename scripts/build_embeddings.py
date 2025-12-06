# calculate embeddings for all passages
# TODO() - semantic_search might be the better way to go about this
# https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html

import os
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Get absolute paths relative to this script's location
BASE_DIR = os.path.join(os.getenv('HOME'), 'argument')
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
INPUT_PASSAGE = os.path.join(PROCESSED_DIR, "passages.csv")
OUTPUT_EMBED = os.path.join(PROCESSED_DIR, "embeddings.pkl")

# from Step 2 output
df = pd.read_csv(INPUT_PASSAGE)

# see documentation on pretrained models
# https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
if os.path.exists(OUTPUT_EMBED):
    print("Embeddings already present.")
else:
    print("Generating embeddings locally with all-MiniLM-L6-v2...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(df["passage"].tolist(), show_progress_bar=True)

    with open(OUTPUT_EMBED, "wb") as f:
        pickle.dump(embeddings, f)

