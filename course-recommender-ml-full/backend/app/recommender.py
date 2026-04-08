# import numpy as np
# # sentence-transformers is optional at runtime
# try:
#     from sentence_transformers import SentenceTransformer
#     _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
# except Exception:
#     _MODEL = None
# from sklearn.metrics.pairwise import cosine_similarity

# async def text_search(q, limit, db):
#     regex = {"$regex": q, "$options":"i"} if q else {"$exists": True}
#     cursor = db.courses.find({"$or":[{"title": regex}, {"description": regex}, {"tags": regex}]}).limit(limit)
#     results = []
#     async for doc in cursor:
#         results.append({
#             "id": str(doc.get("_id")),
#             "title": doc.get("title"),
#             "provider": doc.get("provider"),
#             "price": doc.get("price"),
#             "duration_hours": doc.get("duration_hours"),
#             "url": doc.get("url"),
#             "snippet": doc.get("description","")[:200]
#         })
#     return results

# async def semantic_search(q, limit, db):
#     if _MODEL is None:
#         raise RuntimeError("Semantic search model not available in this backend. Install sentence-transformers to enable it.")
#     q_vec = _MODEL.encode(q, convert_to_numpy=True).reshape(1,-1)
#     cursor = db.courses.find({"embedding": {"$exists": True}})
#     docs = []
#     embs = []
#     async for d in cursor:
#         docs.append(d)
#         embs.append(d.get("embedding"))
#     if not docs:
#         return []
#     embs = np.array(embs)
#     sims = cosine_similarity(q_vec, embs)[0]
#     idxs = sims.argsort()[::-1][:limit]
#     results = []
#     for i in idxs:
#         d = docs[int(i)]
#         results.append({
#             "id": str(d.get("_id")),
#             "title": d.get("title"),
#             "provider": d.get("provider"),
#             "price": d.get("price"),
#             "duration_hours": d.get("duration_hours"),
#             "url": d.get("url"),
#             "score": float(sims[int(i)]),
#             "snippet": d.get("description","")[:200]
#         })
#     return results

# async def recommend_for_user(email, limit, db):
#     user = await db.users.find_one({"email": email}) if email else None
#     if not user:
#         cursor = db.courses.find({}).limit(limit)
#         res=[]
#         async for d in cursor:
#             res.append({"id": str(d.get("_id")), "title": d.get("title"), "provider": d.get("provider"), "url": d.get("url")})
#         return res
#     skills = user.get("skills", {})
#     if skills:
#         top_skill = sorted(skills.items(), key=lambda x: -x[1])[0][0]
#         cursor = db.courses.find({"tags": {"$regex": top_skill, "$options":"i"}}).limit(limit)
#         res=[]
#         async for d in cursor:
#             res.append({"id": str(d.get("_id")), "title": d.get("title"), "provider": d.get("provider"), "url": d.get("url")})
#         if res:
#             return res
#     return await text_search("", limit, db)

# async def generate_learning_path(goal, hours_per_day, db):
#     goal_map = {
#         "data scientist": ["python","statistics","machine learning","deep learning"],
#         "web developer": ["html","css","javascript","react"],
#         "ml engineer": ["python","machine learning","deep learning","deployment"]
#     }
#     skills = goal_map.get((goal or "").lower(), ["python","statistics","machine learning"])
#     path = []
#     total_hours = 0.0
#     for skill in skills:
#         doc = await db.courses.find_one({"tags": {"$regex": skill, "$options":"i"}})
#         if doc:
#             duration = doc.get("duration_hours") or 0
#             path.append({"skill": skill, "course_title": doc.get("title"), "duration_hours": duration, "url": doc.get("url")})
#             total_hours += duration
#     days_needed = max(1, int((total_hours / hours_per_day) + (1 if total_hours % hours_per_day > 0 else 0)))
#     schedule = {"total_hours": total_hours, "days_needed": days_needed, "daily_hours": hours_per_day, "path": path}
#     return schedule
import numpy as np
# sentence-transformers is optional at runtime
try:
    from sentence_transformers import SentenceTransformer
    _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _MODEL = None
from sklearn.metrics.pairwise import cosine_similarity


async def text_search(q, limit, db):
    regex = {"$regex": q, "$options":"i"} if q else {"$exists": True}
    cursor = db.courses.find({"$or":[{"title": regex}, {"description": regex}, {"tags": regex}]}).limit(limit)
    results = []
    async for doc in cursor:
        results.append({
            "id": doc.get("id"),
            "title": doc.get("title"),
            "provider": doc.get("provider"),
            "price": doc.get("price"),
            "duration_hours": doc.get("duration_hours"),
            "url": doc.get("url"),
            "snippet": doc.get("description","")[:200]
        })
    return results


async def semantic_search(q, limit, db):
    if _MODEL is None:
        raise RuntimeError("Semantic search model not available in this backend. Install sentence-transformers to enable it.")
    q_vec = _MODEL.encode(q, convert_to_numpy=True).reshape(1,-1)
    cursor = db.courses.find({"embedding": {"$exists": True}})
    docs = []
    embs = []
    async for d in cursor:
        docs.append(d)
        embs.append(d.get("embedding"))
    if not docs:
        return []
    embs = np.array(embs)
    sims = cosine_similarity(q_vec, embs)[0]
    idxs = sims.argsort()[::-1][:limit]
    results = []
    for i in idxs:
        d = docs[int(i)]
        results.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "provider": d.get("provider"),
            "price": d.get("price"),
            "duration_hours": d.get("duration_hours"),
            "url": d.get("url"),
            "score": float(sims[int(i)]),
            "snippet": d.get("description","")[:200]
        })
    return results


async def recommend_for_user(email, limit, db):
    user = await db.users.find_one({"email": email}) if email else None
    if not user:
        cursor = db.courses.find({}).limit(limit)
        res=[]
        async for d in cursor:
            res.append({
                "id": d.get("id"),
                "title": d.get("title"),
                "provider": d.get("provider"),
                "url": d.get("url")
            })
        return res
    skills = user.get("skills", {})
    if skills:
        top_skill = sorted(skills.items(), key=lambda x: -x[1])[0][0]
        cursor = db.courses.find({"tags": {"$regex": top_skill, "$options":"i"}}).limit(limit)
        res=[]
        async for d in cursor:
            res.append({
                "id": d.get("id"),
                "title": d.get("title"),
                "provider": d.get("provider"),
                "url": d.get("url")
            })
        if res:
            return res
    return await text_search("", limit, db)


async def generate_learning_path(goal, hours_per_day, db):
    goal_map = {
        "data scientist": ["python","statistics","machine learning","deep learning"],
        "web developer": ["html","css","javascript","react"],
        "ml engineer": ["python","machine learning","deep learning","deployment"]
    }
    skills = goal_map.get((goal or "").lower(), ["python","statistics","machine learning"])
    path = []
    total_hours = 0.0
    for skill in skills:
        doc = await db.courses.find_one({"tags": {"$regex": skill, "$options":"i"}})
        if doc:
            duration = doc.get("duration_hours") or 0
            path.append({
                "skill": skill,
                "course_title": doc.get("title"),
                "duration_hours": duration,
                "url": doc.get("url")
            })
            total_hours += duration
    days_needed = max(1, int((total_hours / hours_per_day) + (1 if total_hours % hours_per_day > 0 else 0)))
    schedule = {"total_hours": total_hours, "days_needed": days_needed, "daily_hours": hours_per_day, "path": path}
    return schedule
