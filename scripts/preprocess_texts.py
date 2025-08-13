import os
import csv
import re

# Get absolute paths relative to this script's location
BASE_DIR = os.path.join(os.getenv('HOME'), 'argument')
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "passages.csv")

# Ensure processed directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

def extract_metadata_and_text(file_path):
    author, title = None, None
    text_lines = []
    inside_text = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not inside_text:
                if line.lower().startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.lower().startswith("author:"):
                    author = line.split(":", 1)[1].strip()
                elif "*** start of the project gutenberg" in line.lower():
                    inside_text = True
            else:
                if "*** end of the project gutenberg" in line.lower():
                    break
                text_lines.append(line.strip())

    if not author:
        # Fallback: try filename-based author
        filename = os.path.basename(file_path)
        author = filename.split("_")[0]
    if not title:
        # Fallback: filename-based title
        title = os.path.splitext(filename)[0]

    return author, title, text_lines

def split_into_passages(text_lines):
    passages = []
    buffer = []
    for line in text_lines:
        if line == "":
            if buffer:
                passages.append(" ".join(buffer).strip())
                buffer = []
        else:
            buffer.append(line)
    if buffer:
        passages.append(" ".join(buffer).strip())
    return passages

def main():
    data = []
    file_id = 1

    for filename in os.listdir(RAW_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(RAW_DIR, filename)
            author, title, text_lines = extract_metadata_and_text(file_path)
            passages = split_into_passages(text_lines)

            for idx, passage in enumerate(passages):
                data.append({
                    "id": f"{file_id}_{idx}",
                    "author": author,
                    "work": title,
                    "passage": passage
                })
            file_id += 1

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "author", "work", "passage"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)

    print(f"Processed {len(data)} passages from {len(os.listdir(RAW_DIR))} files.")
    print(f"Output saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

