"""
app.py — Flask Search Engine API + Static UI Server
-----------------------------------------------------
HOW TO RUN (in order):
  1.  pip install flask pyspark
  2.  python pyspark_index.py          # builds inverted_index.json
  3.  python app.py                    # starts Flask on http://127.0.0.1:5000

API:
  GET /search?word=<query>
  Returns: { "word": "...", "documents": [...] }
"""

import json
import os
import re
from flask import Flask, request, jsonify, render_template

# ── App Setup ──────────────────────────────────────────────────────────────────
app   = Flask(__name__)
INDEX = {}                           # in-memory inverted index (loaded once)
INDEX_FILE = "inverted_index.json"


def load_index():
    """Load the pre-built inverted index from JSON into memory."""
    global INDEX
    if not os.path.exists(INDEX_FILE):
        print(f"[WARN] '{INDEX_FILE}' not found. Run pyspark_index.py first.")
        return
    with open(INDEX_FILE, "r", encoding="utf-8") as fh:
        INDEX = json.load(fh)
    print(f"[INFO] Loaded {len(INDEX)} indexed words from '{INDEX_FILE}'.")


def clean_query(word: str) -> str:
    """Normalise a search query — lowercase + strip punctuation."""
    return re.sub(r"[^a-z0-9]", "", word.lower())


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Serve the search UI."""
    return render_template("index.html")


@app.route("/search")
def search():
    """
    GET /search?word=<query>
    Returns JSON with matched documents.
    """
    raw   = request.args.get("word", "").strip()
    query = clean_query(raw)

    if not query:
        return jsonify({"error": "Query parameter 'word' is required."}), 400

    docs = INDEX.get(query, [])
    return jsonify({
        "word":      query,
        "documents": docs,
        "count":     len(docs)
    })


@app.route("/stats")
def stats():
    """Return basic index statistics."""
    return jsonify({
        "total_words":     len(INDEX),
        "index_loaded":    bool(INDEX),
    })


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_index()
    app.run(debug=True, host="0.0.0.0", port=5000)
