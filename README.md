# Milestone 2: Web-based Data Application

## Team

| Student Name | Student ID |
|---|---|
| Ly Chi Hung | s4046014 |
| Le Nguyen Kiet | s4043909 |
| Tran Vu Nhat Tin | s3870729 |
| Phan Hoang Vu | s4192517 |

## Demo Video

- Link: <ADD_DEMO_VIDEO_URL>

## Project Overview

This project delivers an online beauty and cosmetics store that supports:

- Product browsing and keyword search
- ML-assisted review submission with buy/not-buy label and user override
- Similar product recommendations
- Additional functionality (wishlist + sentiment summary)

## Requirements

- Python 3.10+
- Node.js 18+

## Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python data/seed.py
uvicorn app.main:app --reload
```

API: http://localhost:8000

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

## Notes

- The backend loads pre-trained ML models from backend/ml/models.
- If you need to reset data, delete backend/beauty_shop.db and re-run seed.py.

## Submission Checklist

- Source code and interface
- Demo video (.mp4) link
- README with team details and run instructions
- Any large data files linked via OneDrive if needed
