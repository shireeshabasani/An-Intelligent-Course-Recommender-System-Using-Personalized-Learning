

import os
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")

try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    MODEL = None

async def load_seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_default_database()
    await db.courses.delete_many({})
    here = os.path.join(os.path.dirname(__file__), "../backend/app/courses_dataset.json")
    with open(here, "r", encoding="utf-8") as f:
        docs = json.load(f)
    for doc in docs:
        if MODEL:
            text = doc.get('title', '') + " " + doc.get('description', '')
            doc['embedding'] = MODEL.encode(text).tolist()
    if docs:
        await db.courses.insert_many(docs)
        print(f"Inserted {len(docs)} docs (embeddings={'yes' if MODEL else 'no'})")
    client.close()

if __name__ == "__main__":
    asyncio.run(load_seed())
