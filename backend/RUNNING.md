# Running the Project

## Setup (once)

```bash
pip install -r requirements.txt
python data/seed.py
```

## Start the server

```bash
uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

## Notes

- ML models in `ml/models/` are pre-trained — no training step needed.
- The server loads all models and builds the search/recommendation indexes on startup automatically.
- To reset the database, delete `beauty_shop.db` and re-run `data/seed.py`.
