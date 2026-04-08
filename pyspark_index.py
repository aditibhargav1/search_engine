"""
pyspark_index.py — Distributed Inverted Index using PySpark MapReduce
----------------------------------------------------------------------
HOW TO RUN:
  pip install pyspark
  python pyspark_index.py

OUTPUT:
  inverted_index.json  — word → [doc1, doc2, ...] mapping
"""

import os
import re
import json
from pyspark import SparkContext, SparkConf

# Set environment variables BEFORE Spark starts
os.environ["JAVA_HOME"] = r"C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot"
os.environ["PYSPARK_PYTHON"] = r"C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe"
# ── Configuration ──────────────────────────────────────────────────────────────
DOCS_FOLDER   = "documents"          # folder containing .txt files
OUTPUT_FILE   = "inverted_index.json"
APP_NAME      = "DistributedSearchIndexer"


def clean_word(word: str) -> str:
    """Strip punctuation and lowercase a word."""
    return re.sub(r"[^a-z0-9]", "", word.lower())


def build_inverted_index():
    # ── Spark Setup ────────────────────────────────────────────────────────────
    conf = SparkConf().setAppName(APP_NAME).setMaster("local[*]")
    sc   = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")          # suppress noisy INFO logs

    # ── Load all .txt files from documents/ ───────────────────────────────────
    doc_files = [
        os.path.join(DOCS_FOLDER, f)
        for f in os.listdir(DOCS_FOLDER)
        if f.endswith(".txt")
    ]

    if not doc_files:
        print(f"[ERROR] No .txt files found in '{DOCS_FOLDER}/'")
        sc.stop()
        return

    print(f"[INFO] Indexing {len(doc_files)} document(s): {[os.path.basename(f) for f in doc_files]}")

    # ── MapReduce Pipeline ─────────────────────────────────────────────────────
    # Step 1 — Load each file as an RDD of (doc_name, line) pairs
    def file_to_pairs(filepath):
        doc_name = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        return [(doc_name, line) for line in lines]

    doc_rdd = sc.parallelize(doc_files).flatMap(file_to_pairs)

    # Step 2 — flatMap: (doc, line) → [(word, doc), (word, doc), ...]
    word_doc_pairs = doc_rdd.flatMap(
        lambda doc_line: [
            (clean_word(token), doc_line[0])
            for token in doc_line[1].split()
            if clean_word(token)                # skip empty strings after cleaning
        ]
    )

    # Step 3 — map: deduplicate (word, doc) pairs per document
    unique_pairs = word_doc_pairs.distinct()

    # Step 4 — map each pair to (word, [doc]) for reduction
    word_to_list = unique_pairs.map(lambda wd: (wd[0], [wd[1]]))

    # Step 5 — reduceByKey: merge document lists per word
    inverted_index_rdd = word_to_list.reduceByKey(lambda a, b: sorted(set(a + b)))

    # ── Collect & Persist ──────────────────────────────────────────────────────
    inverted_index = dict(inverted_index_rdd.sortByKey().collect())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(inverted_index, out, indent=2)

    print(f"[INFO] Index built. {len(inverted_index)} unique words → '{OUTPUT_FILE}'")
    sc.stop()


if __name__ == "__main__":
    build_inverted_index()
