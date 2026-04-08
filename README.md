# search_engine
# NEXUS — Distributed Search Engine

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the inverted index (MapReduce via PySpark)
python pyspark_index.py

# 3. Start the Flask server
python app.py

# 4. Open browser → http://127.0.0.1:5000
```

## Project Structure

```
search_engine/
├── app.py                    # Flask API + server
├── pyspark_index.py          # PySpark MapReduce indexer
├── inverted_index.json       # Generated index (after step 2)
├── requirements.txt
├── documents/                # Source text files
│   ├── machine_learning.txt
│   ├── big_data.txt
│   ├── python_programming.txt
│   ├── search_engines.txt
│   └── algorithms.txt
├── templates/
│   └── index.html            # Search UI
└── static/
    ├── style.css
    └── script.js
```

## API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Search UI |
| `/search?word=<query>` | GET | Search index |
| `/stats` | GET | Index statistics |

## Adding Documents

Drop any `.txt` file into `documents/` and re-run `pyspark_index.py`.
