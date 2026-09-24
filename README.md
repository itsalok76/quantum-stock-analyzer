# Quantum Stock Analyzer - Startup Guide

This project has multiple version folders. The service for version 11.0.1 is under:

- `version-11.0.1/stock-analysis`

## Start the service

From the project root, run:

```bash
cd version-11.0.1/stock-analysis
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.headless true --server.port 8501
```

Then open this URL in your browser:

```text
http://localhost:8501
```

## Important note

Do not run Streamlit from the main workspace root. The app file is inside the `version-11.0.1/stock-analysis` folder, so you must first `cd` into that folder.

## Optional: create a virtual environment

```bash
cd version-11.0.1/stock-analysis
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.headless true --server.port 8501
```

## Stop the service

Press:

```text
Ctrl + C
```

in the terminal where the Streamlit process is running.
