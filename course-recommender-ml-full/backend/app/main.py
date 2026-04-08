"""import json
import os
import csv
from math import ceil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# ---------------- CONFIG ----------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="LMS Unified Backend - Final Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class UserIn(BaseModel):
    email: str
    password: str
    available_hours_per_day: float = 1


class AddCourseIn(BaseModel):
    course_id: str
    title: str
    hours: float
    url: str = ""


# ---------------- BADGE UTILITY ----------------

async def award_badge(email: str, badge_name: str):
    email = email.lower().strip()

    record = {
        "email": email,
        "badge_name": badge_name,
        "name": badge_name,
        "awarded_at": datetime.utcnow()
    }

    await db.user_badges.update_one(
        {"email": email, "badge_name": badge_name},
        {"$set": record},
        upsert=True
    )


# ---------------- STARTUP SEED ----------------

@app.on_event("startup")
async def startup_event():

    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index(
        [("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    await db.quiz_results.create_index(
        [("email", 1), ("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    try:
        await db.courses.drop_index("id_1")
    except Exception:
        pass

    await db.courses.create_index("id", unique=True)

    current_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(os.path.dirname(current_file))
    data_dir = os.path.join(backend_dir, "data")

    print("Searching data in:", data_dir)

    # -------- Load Quizzes --------

    quiz_path = os.path.join(data_dir, "quizzes.json")

    if os.path.exists(quiz_path):

        with open(quiz_path, "r") as f:
            quizzes = json.load(f)

            for q in quizzes:

                q["quiz_number"] = int(q["quiz_number"])

                await db.quizzes.update_one(
                    {
                        "course_id": q["course_id"],
                        "quiz_number": q["quiz_number"]
                    },
                    {"$set": q},
                    upsert=True
                )

        print("Quizzes loaded:", len(quizzes))

    # -------- Load Courses --------

    csv_path = os.path.join(data_dir, "seed.csv")

    if os.path.exists(csv_path):

        with open(csv_path, encoding="utf-8") as f:

            reader = csv.DictReader(f)
            count = 0

            for row in reader:

                row["duration_hours"] = float(row.get("duration_hours", 1))
                row["price"] = float(row.get("price", 0))

                await db.courses.update_one(
                    {"id": row["id"]},
                    {"$set": row},
                    upsert=True
                )

                count += 1

        print("Courses loaded:", count)


# ---------------- AUTH ----------------

@app.post("/auth/register")
async def register(u: UserIn):

    email = u.email.lower().strip()

    existing = await db.users.find_one({"email": email})

    if existing:
        raise HTTPException(400, "Email already registered")

    user_data = u.dict()
    user_data["email"] = email
    user_data["streak"] = 1
    user_data["learning_path"] = []
    user_data["skills"] = []

    await db.users.insert_one(user_data)

    return {"msg": "ok"}


@app.post("/auth/login")
async def login(u: UserIn):

    user = await db.users.find_one({"email": u.email.lower().strip()})

    if not user or user["password"] != u.password:
        raise HTTPException(401, "Invalid credentials")

    return {
        "msg": "ok",
        "user": {
            "email": user["email"],
            "available_hours_per_day": user.get(
                "available_hours_per_day", 1
            )
        }
    }


# ---------------- GET USER ----------------

@app.get("/users/{email}")
async def get_user(email: str):

    email = email.lower().strip()

    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    user["_id"] = str(user["_id"])

    return user


# ---------------- UPDATE USER SKILLS ----------------
@app.put("/users/{email}/skills")
async def update_skills(email: str, skills: list = Body(...)):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    # Normalize skills to lowercase to ensure consistency
    normalized_skills = list({s.strip().lower() for s in skills if s.strip()})

    await db.users.update_one(
        {"email": email},
        {"$set": {"skills": normalized_skills}}
    )

    return {"msg": "skills updated", "skills": normalized_skills}

# ---------------- SKILL GAP ANALYSIS ----------------
@app.get("/users/{email}/skill-gap")
async def skill_gap(email: str, role: str):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    user_skills = [s.lower() for s in user.get("skills", [])]  # normalize

    # ---------------- Define Skills for All Roles ----------------
    role_skills = {
        "Data Scientist": [
            "python", "machine learning", "statistics", "pandas",
            "numpy", "deep learning", "matplotlib", "scikit-learn"
        ],
        "Web Developer": [
            "html", "css", "javascript", "react", "node.js",
            "rest api", "frontend", "backend"
        ],
        "ML Engineer": [
            "python", "machine learning", "deep learning",
            "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"
        ],
        "DevOps Engineer": [
            "docker", "kubernetes", "ci/cd", "linux",
            "aws", "azure", "gcp", "terraform", "monitoring"
        ],
        "Cloud Architect": [
            "aws", "azure", "gcp", "cloud computing",
            "networking", "security", "scalability", "architecture design"
        ],
        "Frontend Developer": [
            "html", "css", "javascript", "react",
            "vue.js", "angular", "ui/ux", "responsive design"
        ],
        "Backend Developer": [
            "node.js", "express.js", "java", "python",
            "rest api", "database", "sql", "mongodb"
        ],
        "Database Administrator": [
            "sql", "mongodb", "database design",
            "backup", "replication", "indexing",
            "performance tuning", "security"
        ]
    }

    required_skills = role_skills.get(role, [])

    # ---------------- Match Skills Case-Insensitive ----------------
    existing_skills = [
        s for s in required_skills if s.lower() in user_skills
    ]

    missing_skills = [
        s for s in required_skills if s.lower() not in user_skills
    ]

    return {
        "role": role,
        "your_skills": user.get("skills", []),
        "required_skills": required_skills,
        "existing_skills": existing_skills,
        "missing_skills": missing_skills,
        "skill_gap_count": len(missing_skills)
    }
# ---------------- SEARCH ----------------

@app.get("/search")
async def search(q: str = ""):

    if not q:
        return {"results": []}

    query = {
        "title": {
            "$regex": q.strip(),
            "$options": "i"
        }
    }

    cursor = db.courses.find(query)
    results = await cursor.to_list(10)

    for c in results:
        c["_id"] = str(c["_id"])

    return {"results": results}


# ---------------- ADD COURSE ----------------

@app.post("/users/{email}/add-course")
async def add_course(email: str, course: AddCourseIn):

    email = email.lower().strip()

    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    daily_hours = float(user.get("available_hours_per_day", 1))
    course_hours = float(course.hours)

    total_days = ceil(course_hours / daily_hours)

    roadmap = [
        {"step": 1, "task": "Foundations", "duration": f"{ceil(total_days*0.2)} days"},
        {"step": 2, "task": "Core Learning", "duration": f"{ceil(total_days*0.5)} days"},
        {"step": 3, "task": "Project", "duration": f"{ceil(total_days*0.3)} days"},
    ]

    new_course = {
        **course.dict(),
        "days_to_complete": total_days,
        "roadmap": roadmap,
        "added_at": datetime.utcnow()
    }

    await db.users.update_one(
        {"email": email},
        {"$push": {"learning_path": new_course}}
    )

    await award_badge(email, "Course Explorer")

    return {"msg": "ok", "course": new_course}


# ---------------- ACTIVITY ----------------

@app.get("/users/{email}/activity")
async def activity(email: str):

    user = await db.users.find_one({"email": email.lower().strip()})

    if not user:
        return {"streak": 0, "learning_path": []}

    return {
        "streak": user.get("streak", 0),
        "learning_path": user.get("learning_path", [])
    }


# ---------------- BADGES ----------------

@app.get("/users/{email}/badges")
async def badges(email: str):

    cursor = db.user_badges.find({"email": email.lower().strip()})
    badges = await cursor.to_list(100)

    for b in badges:
        b["_id"] = str(b["_id"])

    return {"badges": badges}


# ---------------- QUIZ ----------------

@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):

    quiz = await db.quizzes.find_one(
        {"course_id": course_id, "quiz_number": quiz_num}
    )

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    quiz["_id"] = str(quiz["_id"])

    for q in quiz["questions"]:
        q.pop("answer", None)

    return quiz


# ---------------- SUBMIT QUIZ ----------------

@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):

    email = payload["email"].lower().strip()
    course_id = payload["course_id"]
    quiz_num = int(payload["quiz_number"])
    answers = payload["answers"]

    quiz = await db.quizzes.find_one(
        {"course_id": course_id, "quiz_number": quiz_num}
    )

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    questions = quiz["questions"]

    correct = 0

    for i, q in enumerate(questions):
        if i < len(answers) and answers[i] == q["answer"]:
            correct += 1

    percent = correct / len(questions) * 100

    result = {
        "email": email,
        "course_id": course_id,
        "quiz_number": quiz_num,
        "score": correct,
        "total": len(questions),
        "percentage": percent,
        "completed_at": datetime.utcnow()
    }

    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result},
        upsert=True
    )

    if percent >= 80:
        await award_badge(email, "Quiz Master")

    return result"""
"""import json
import os
import csv
from math import ceil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# ---------------- CONFIG ----------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="LMS Unified Backend - Final Version with Quiz Persistence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class UserIn(BaseModel):
    email: str
    password: str
    available_hours_per_day: float = 1


class AddCourseIn(BaseModel):
    course_id: str
    title: str
    hours: float
    url: str = ""


# ---------------- BADGE UTILITY ----------------

async def award_badge(email: str, badge_name: str):
    email = email.lower().strip()

    record = {
        "email": email,
        "badge_name": badge_name,
        "name": badge_name,
        "awarded_at": datetime.utcnow()
    }

    await db.user_badges.update_one(
        {"email": email, "badge_name": badge_name},
        {"$set": record},
        upsert=True
    )


# ---------------- STARTUP SEED ----------------

@app.on_event("startup")
async def startup_event():

    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index(
        [("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    await db.quiz_results.create_index(
        [("email", 1), ("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    try:
        await db.courses.drop_index("id_1")
    except Exception:
        pass

    await db.courses.create_index("id", unique=True)

    current_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(os.path.dirname(current_file))
    data_dir = os.path.join(backend_dir, "data")

    # -------- Load Quizzes --------
    quiz_path = os.path.join(data_dir, "quizzes.json")
    if os.path.exists(quiz_path):
        with open(quiz_path, "r") as f:
            quizzes = json.load(f)
            for q in quizzes:
                q["quiz_number"] = int(q["quiz_number"])
                await db.quizzes.update_one(
                    {"course_id": q["course_id"], "quiz_number": q["quiz_number"]},
                    {"$set": q},
                    upsert=True
                )

    # -------- Load Courses --------
    csv_path = os.path.join(data_dir, "seed.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["duration_hours"] = float(row.get("duration_hours", 1))
                row["price"] = float(row.get("price", 0))
                await db.courses.update_one(
                    {"id": row["id"]},
                    {"$set": row},
                    upsert=True
                )


# ---------------- AUTH ----------------

@app.post("/auth/register")
async def register(u: UserIn):
    email = u.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(400, "Email already registered")
    user_data = u.dict()
    user_data["email"] = email
    user_data["streak"] = 1
    user_data["learning_path"] = []
    user_data["skills"] = []
    await db.users.insert_one(user_data)
    return {"msg": "ok"}


@app.post("/auth/login")
async def login(u: UserIn):
    user = await db.users.find_one({"email": u.email.lower().strip()})
    if not user or user["password"] != u.password:
        raise HTTPException(401, "Invalid credentials")
    return {
        "msg": "ok",
        "user": {
            "email": user["email"],
            "available_hours_per_day": user.get("available_hours_per_day", 1)
        }
    }


# ---------------- GET USER ----------------

@app.get("/users/{email}")
async def get_user(email: str):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")
    user["_id"] = str(user["_id"])
    return user


# ---------------- UPDATE USER SKILLS ----------------

@app.put("/users/{email}/skills")
async def update_skills(email: str, skills: list = Body(...)):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")
    normalized_skills = list({s.strip().lower() for s in skills if s.strip()})
    await db.users.update_one({"email": email}, {"$set": {"skills": normalized_skills}})
    return {"msg": "skills updated", "skills": normalized_skills}


# ---------------- SKILL GAP ANALYSIS ----------------

@app.get("/users/{email}/skill-gap")
async def skill_gap(email: str, role: str):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")

    user_skills = [s.lower() for s in user.get("skills", [])]
    role_skills = {
        "Data Scientist": ["python", "machine learning", "statistics", "pandas", "numpy", "deep learning", "matplotlib", "scikit-learn"],
        "Web Developer": ["html", "css", "javascript", "react", "node.js", "rest api", "frontend", "backend"],
        "ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"],
        "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "linux", "aws", "azure", "gcp", "terraform", "monitoring"],
        "Cloud Architect": ["aws", "azure", "gcp", "cloud computing", "networking", "security", "scalability", "architecture design"],
        "Frontend Developer": ["html", "css", "javascript", "react", "vue.js", "angular", "ui/ux", "responsive design"],
        "Backend Developer": ["node.js", "express.js", "java", "python", "rest api", "database", "sql", "mongodb"],
        "Database Administrator": ["sql", "mongodb", "database design", "backup", "replication", "indexing", "performance tuning", "security"]
    }

    required_skills = role_skills.get(role, [])
    existing_skills = [s for s in required_skills if s.lower() in user_skills]
    missing_skills = [s for s in required_skills if s.lower() not in user_skills]

    return {
        "role": role,
        "your_skills": user.get("skills", []),
        "required_skills": required_skills,
        "existing_skills": existing_skills,
        "missing_skills": missing_skills,
        "skill_gap_count": len(missing_skills)
    }


# ---------------- SEARCH ----------------

@app.get("/search")
async def search(q: str = ""):
    if not q:
        return {"results": []}
    query = {"title": {"$regex": q.strip(), "$options": "i"}}
    cursor = db.courses.find(query)
    results = await cursor.to_list(10)
    for c in results:
        c["_id"] = str(c["_id"])
    return {"results": results}


# ---------------- ADD COURSE ----------------

@app.post("/users/{email}/add-course")
async def add_course(email: str, course: AddCourseIn):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")

    daily_hours = float(user.get("available_hours_per_day", 1))
    course_hours = float(course.hours)
    total_days = ceil(course_hours / daily_hours)

    roadmap = [
        {"step": 1, "task": "Foundations", "duration": f"{ceil(total_days*0.2)} days"},
        {"step": 2, "task": "Core Learning", "duration": f"{ceil(total_days*0.5)} days"},
        {"step": 3, "task": "Project", "duration": f"{ceil(total_days*0.3)} days"},
    ]

    new_course = {
        **course.dict(),
        "days_to_complete": total_days,
        "roadmap": roadmap,
        "added_at": datetime.utcnow()
    }

    await db.users.update_one({"email": email}, {"$push": {"learning_path": new_course}})
    await award_badge(email, "Course Explorer")
    return {"msg": "ok", "course": new_course}


# ---------------- ACTIVITY ----------------

@app.get("/users/{email}/activity")
async def activity(email: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user:
        return {"streak": 0, "learning_path": []}
    return {"streak": user.get("streak", 0), "learning_path": user.get("learning_path", [])}


# ---------------- BADGES ----------------

@app.get("/users/{email}/badges")
async def badges(email: str):
    cursor = db.user_badges.find({"email": email.lower().strip()})
    badges = await cursor.to_list(100)
    for b in badges:
        b["_id"] = str(b["_id"])
    return {"badges": badges}


# ---------------- QUIZ ----------------

@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    quiz["_id"] = str(quiz["_id"])
    for q in quiz["questions"]:
        q.pop("answer", None)
    return quiz


# ---------------- QUIZ STATUS (PERSISTENCE) ----------------

@app.get("/quiz/status")
async def get_quiz_status(email: str, course_id: str, quiz_num: int):
    email = email.lower().strip()
    result = await db.quiz_results.find_one({"email": email, "course_id": course_id, "quiz_number": quiz_num})
    
    if not result:
        return {"completed": False}

    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz:
        return {"completed": False}
    
    details = []
    user_answers = result.get("answers", [])
    for i, q in enumerate(quiz["questions"]):
        user_ans = user_answers[i] if i < len(user_answers) else -1
        details.append({
            "question": q["question"],
            "options": q["options"],
            "user_answer": user_ans,
            "correct_answer": q["answer"],
            "is_correct": user_ans == q["answer"]
        })

    return {
        "completed": True,
        "previous_result": {
            "score": result["score"],
            "total": result["total"],
            "percentage": result["percentage"],
            "passed": result["percentage"] >= 80,
            "details": details
        }
    }


# ---------------- SUBMIT QUIZ ----------------

@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id = payload["course_id"]
    quiz_num = int(payload["quiz_number"])
    answers = payload["answers"]

    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    questions = quiz["questions"]
    correct = 0
    details = []

    for i, q in enumerate(questions):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct:
            correct += 1
            
        details.append({
            "question": q["question"],
            "options": q["options"],
            "user_answer": user_ans,
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    percent = (correct / len(questions)) * 100
    result_entry = {
        "email": email,
        "course_id": course_id,
        "quiz_number": quiz_num,
        "score": correct,
        "total": len(questions),
        "percentage": percent,
        "answers": answers, 
        "completed_at": datetime.utcnow()
    }

    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry},
        upsert=True
    )

    if percent >= 80:
        await award_badge(email, "Quiz Master")

    return {
        "score": correct,
        "total": len(questions),
        "percentage": percent,
        "passed": percent >= 80,
        "details": details
    }"""
"""import json
import os
import csv
from math import ceil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# ---------------- CONFIG ----------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="LMS Unified Backend - Final Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class UserIn(BaseModel):
    email: str
    password: str
    available_hours_per_day: float = 1


class AddCourseIn(BaseModel):
    course_id: str
    title: str
    hours: float
    url: str = ""


# ---------------- BADGE UTILITY ----------------

async def award_badge(email: str, badge_name: str):
    email = email.lower().strip()

    record = {
        "email": email,
        "badge_name": badge_name,
        "name": badge_name,
        "awarded_at": datetime.utcnow()
    }

    await db.user_badges.update_one(
        {"email": email, "badge_name": badge_name},
        {"$set": record},
        upsert=True
    )


# ---------------- STARTUP SEED ----------------

@app.on_event("startup")
async def startup_event():

    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index(
        [("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    await db.quiz_results.create_index(
        [("email", 1), ("course_id", 1), ("quiz_number", 1)],
        unique=True
    )

    try:
        await db.courses.drop_index("id_1")
    except Exception:
        pass

    await db.courses.create_index("id", unique=True)

    current_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(os.path.dirname(current_file))
    data_dir = os.path.join(backend_dir, "data")

    print("Searching data in:", data_dir)

    # -------- Load Quizzes --------

    quiz_path = os.path.join(data_dir, "quizzes.json")

    if os.path.exists(quiz_path):

        with open(quiz_path, "r") as f:
            quizzes = json.load(f)

            for q in quizzes:

                q["quiz_number"] = int(q["quiz_number"])

                await db.quizzes.update_one(
                    {
                        "course_id": q["course_id"],
                        "quiz_number": q["quiz_number"]
                    },
                    {"$set": q},
                    upsert=True
                )

        print("Quizzes loaded:", len(quizzes))

    # -------- Load Courses --------

    csv_path = os.path.join(data_dir, "seed.csv")

    if os.path.exists(csv_path):

        with open(csv_path, encoding="utf-8") as f:

            reader = csv.DictReader(f)
            count = 0

            for row in reader:

                row["duration_hours"] = float(row.get("duration_hours", 1))
                row["price"] = float(row.get("price", 0))

                await db.courses.update_one(
                    {"id": row["id"]},
                    {"$set": row},
                    upsert=True
                )

                count += 1

        print("Courses loaded:", count)


# ---------------- AUTH ----------------

@app.post("/auth/register")
async def register(u: UserIn):

    email = u.email.lower().strip()

    existing = await db.users.find_one({"email": email})

    if existing:
        raise HTTPException(400, "Email already registered")

    user_data = u.dict()
    user_data["email"] = email
    user_data["streak"] = 1
    user_data["learning_path"] = []
    user_data["skills"] = []

    await db.users.insert_one(user_data)

    return {"msg": "ok"}


@app.post("/auth/login")
async def login(u: UserIn):

    user = await db.users.find_one({"email": u.email.lower().strip()})

    if not user or user["password"] != u.password:
        raise HTTPException(401, "Invalid credentials")

    return {
        "msg": "ok",
        "user": {
            "email": user["email"],
            "available_hours_per_day": user.get(
                "available_hours_per_day", 1
            )
        }
    }


# ---------------- GET USER ----------------

@app.get("/users/{email}")
async def get_user(email: str):

    email = email.lower().strip()

    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    user["_id"] = str(user["_id"])

    return user


# ---------------- UPDATE USER SKILLS ----------------
@app.put("/users/{email}/skills")
async def update_skills(email: str, skills: list = Body(...)):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    # Normalize skills to lowercase to ensure consistency
    normalized_skills = list({s.strip().lower() for s in skills if s.strip()})

    await db.users.update_one(
        {"email": email},
        {"$set": {"skills": normalized_skills}}
    )

    return {"msg": "skills updated", "skills": normalized_skills}

# ---------------- SKILL GAP ANALYSIS ----------------
@app.get("/users/{email}/skill-gap")
async def skill_gap(email: str, role: str):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    user_skills = [s.lower() for s in user.get("skills", [])]  # normalize

    # ---------------- Define Skills for All Roles ----------------
    role_skills = {
        "Data Scientist": [
            "python", "machine learning", "statistics", "pandas",
            "numpy", "deep learning", "matplotlib", "scikit-learn"
        ],
        "Web Developer": [
            "html", "css", "javascript", "react", "node.js",
            "rest api", "frontend", "backend"
        ],
        "ML Engineer": [
            "python", "machine learning", "deep learning",
            "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"
        ],
        "DevOps Engineer": [
            "docker", "kubernetes", "ci/cd", "linux",
            "aws", "azure", "gcp", "terraform", "monitoring"
        ],
        "Cloud Architect": [
            "aws", "azure", "gcp", "cloud computing",
            "networking", "security", "scalability", "architecture design"
        ],
        "Frontend Developer": [
            "html", "css", "javascript", "react",
            "vue.js", "angular", "ui/ux", "responsive design"
        ],
        "Backend Developer": [
            "node.js", "express.js", "java", "python",
            "rest api", "database", "sql", "mongodb"
        ],
        "Database Administrator": [
            "sql", "mongodb", "database design",
            "backup", "replication", "indexing",
            "performance tuning", "security"
        ]
    }

    required_skills = role_skills.get(role, [])

    # ---------------- Match Skills Case-Insensitive ----------------
    existing_skills = [
        s for s in required_skills if s.lower() in user_skills
    ]

    missing_skills = [
        s for s in required_skills if s.lower() not in user_skills
    ]

    return {
        "role": role,
        "your_skills": user.get("skills", []),
        "required_skills": required_skills,
        "existing_skills": existing_skills,
        "missing_skills": missing_skills,
        "skill_gap_count": len(missing_skills)
    }
# ---------------- SEARCH ----------------

@app.get("/search")
async def search(q: str = ""):

    if not q:
        return {"results": []}

    query = {
        "title": {
            "$regex": q.strip(),
            "$options": "i"
        }
    }

    cursor = db.courses.find(query)
    results = await cursor.to_list(10)

    for c in results:
        c["_id"] = str(c["_id"])

    return {"results": results}


# ---------------- ADD COURSE ----------------

@app.post("/users/{email}/add-course")
async def add_course(email: str, course: AddCourseIn):

    email = email.lower().strip()

    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(404, "User not found")

    daily_hours = float(user.get("available_hours_per_day", 1))
    course_hours = float(course.hours)

    total_days = ceil(course_hours / daily_hours)

    roadmap = [
        {"step": 1, "task": "Foundations", "duration": f"{ceil(total_days*0.2)} days"},
        {"step": 2, "task": "Core Learning", "duration": f"{ceil(total_days*0.5)} days"},
        {"step": 3, "task": "Project", "duration": f"{ceil(total_days*0.3)} days"},
    ]

    new_course = {
        **course.dict(),
        "days_to_complete": total_days,
        "roadmap": roadmap,
        "added_at": datetime.utcnow()
    }

    await db.users.update_one(
        {"email": email},
        {"$push": {"learning_path": new_course}}
    )

    await award_badge(email, "Course Explorer")

    return {"msg": "ok", "course": new_course}


# ---------------- ACTIVITY ----------------

@app.get("/users/{email}/activity")
async def activity(email: str):

    user = await db.users.find_one({"email": email.lower().strip()})

    if not user:
        return {"streak": 0, "learning_path": []}

    return {
        "streak": user.get("streak", 0),
        "learning_path": user.get("learning_path", [])
    }


# ---------------- BADGES ----------------

@app.get("/users/{email}/badges")
async def badges(email: str):

    cursor = db.user_badges.find({"email": email.lower().strip()})
    badges = await cursor.to_list(100)

    for b in badges:
        b["_id"] = str(b["_id"])

    return {"badges": badges}


# ---------------- QUIZ ----------------

@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):

    quiz = await db.quizzes.find_one(
        {"course_id": course_id, "quiz_number": quiz_num}
    )

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    quiz["_id"] = str(quiz["_id"])

    for q in quiz["questions"]:
        q.pop("answer", None)

    return quiz


# ---------------- SUBMIT QUIZ ----------------

@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):

    email = payload["email"].lower().strip()
    course_id = payload["course_id"]
    quiz_num = int(payload["quiz_number"])
    answers = payload["answers"]

    quiz = await db.quizzes.find_one(
        {"course_id": course_id, "quiz_number": quiz_num}
    )

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    questions = quiz["questions"]

    correct = 0

    for i, q in enumerate(questions):
        if i < len(answers) and answers[i] == q["answer"]:
            correct += 1

    percent = correct / len(questions) * 100

    result = {
        "email": email,
        "course_id": course_id,
        "quiz_number": quiz_num,
        "score": correct,
        "total": len(questions),
        "percentage": percent,
        "completed_at": datetime.utcnow()
    }

    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result},
        upsert=True
    )

    if percent >= 80:
        await award_badge(email, "Quiz Master")

    return result"""
import json
import os
import csv
from math import ceil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# ---------------- CONFIG ----------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="LMS Unified Backend - Production Ready")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class UserIn(BaseModel):
    email: str
    password: str
    available_hours_per_day: float = 1

class AddCourseIn(BaseModel):
    course_id: str
    title: str
    hours: float
    url: str = ""

# ---------------- UTILS ----------------

async def award_badge(email: str, badge_name: str):
    email = email.lower().strip()
    record = {
        "email": email,
        "badge_name": badge_name,
        "name": badge_name,
        "awarded_at": datetime.utcnow()
    }
    await db.user_badges.update_one(
        {"email": email, "badge_name": badge_name},
        {"$set": record},
        upsert=True
    )

# ---------------- STARTUP SEED ----------------

"""@app.on_event("startup")
async def startup_event():
    # 1. Setup Indexes
    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index([("course_id", 1), ("quiz_number", 1)], unique=True)
    await db.courses.create_index("id", unique=True)
    await db.quiz_results.create_index([("email", 1), ("course_id", 1), ("quiz_number", 1)], unique=True)

    # 2. Path Resolution
    current_file = os.path.abspath(__file__) 
    app_dir = os.path.dirname(current_file)
    backend_dir = os.path.dirname(app_dir)
    data_dir = os.path.join(backend_dir, "data")

    # 3. CRITICAL: Clear old quizzes for a fresh sync of 10-question levels
    await db.quizzes.delete_many({})
    print("🧹 Database cleared for fresh 10-question sync")

    # -------- Load Quizzes --------
   # -------- Load Quizzes with Error Handling --------
    quiz_path = os.path.join(data_dir, "quizzes.json")
    if os.path.exists(quiz_path):
        try:
            with open(quiz_path, "r") as f:
                quizzes = json.load(f)
                count = 0
                for q in quizzes:
                    # Ensure quiz_number is an integer for indexing
                    q["quiz_number"] = int(q["quiz_number"])
                    await db.quizzes.update_one(
                        {"course_id": q["course_id"], "quiz_number": q["quiz_number"]},
                        {"$set": q},
                        upsert=True
                    )
                    count += 1
                print(f"🚀 SUCCESS: Loaded {count} quiz levels from {quiz_path}")
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: quizzes.json has a syntax error: {e}")
        except Exception as e:
            print(f"❌ ERROR: Failed to load quizzes: {e}")

    # -------- Load Courses --------
    csv_path = os.path.join(data_dir, "seed.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                course_id = row.get("id") or row.get("course_id")
                if not course_id: continue
                row["duration_hours"] = float(row.get("duration_hours", 1))
                row["price"] = float(row.get("price", 0))
                await db.courses.update_one({"id": course_id}, {"$set": row}, upsert=True)
            print(f"✅ Courses seeded from {csv_path}")"""
@app.on_event("startup")
async def startup_event():
    # 1. Setup Indexes
    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index([("course_id", 1), ("quiz_number", 1)], unique=True)
    
    # 2. Path Resolution: Go UP from backend to find data
    # os.path.abspath(__file__) -> /project/backend/main.py
    # dirname -> /project/backend
    # dirname again -> /project (the parent folder)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    data_dir = os.path.join(project_root, "data")
    
    print(f"🔍 Searching for data in: {data_dir}")

    # 3. Fresh Sync
    await db.quizzes.delete_many({})

    async def load_json(filename, is_roadmap=False):
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for q in data:
                        c_id = "roadmap" if is_roadmap else q["course_id"]
                        q["quiz_number"] = int(q["quiz_number"])
                        await db.quizzes.update_one(
                            {"course_id": c_id, "quiz_number": q["quiz_number"]},
                            {"$set": q},
                            upsert=True
                        )
                print(f"🚀 SUCCESS: Loaded {len(data)} items from {filename}")
            except Exception as e:
                print(f"❌ JSON ERROR in {filename}: {e}")
        else:
            print(f"⚠️ FILE NOT FOUND: {path}")

    # Load both files from the folder outside 'backend'
    await load_json("quizzes.json", is_roadmap=False)
    await load_json("roadmap_quizzes.json", is_roadmap=True)

# ---------------- AUTH & USERS ----------------

@app.post("/auth/register")
async def register(u: UserIn):
    email = u.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing: raise HTTPException(400, "Email already registered")
    user_data = u.dict()
    user_data.update({"email": email, "streak": 1, "learning_path": [], "skills": []})
    await db.users.insert_one(user_data)
    return {"msg": "ok"}

@app.post("/auth/login")
async def login(u: UserIn):
    user = await db.users.find_one({"email": u.email.lower().strip()})
    if not user or user["password"] != u.password:
        raise HTTPException(401, "Invalid credentials")
    return {"msg": "ok", "user": {"email": user["email"], "available_hours_per_day": user.get("available_hours_per_day", 1)}}

@app.get("/users/{email}")
async def get_user(email: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: raise HTTPException(404, "User not found")
    user["_id"] = str(user["_id"])
    return user

# ---------------- SKILLS & SEARCH ----------------

@app.put("/users/{email}/skills")
async def update_skills(email: str, skills: list = Body(...)):
    email = email.lower().strip()
    normalized = list({s.strip().lower() for s in skills if s.strip()})
    await db.users.update_one({"email": email}, {"$set": {"skills": normalized}})
    return {"msg": "skills updated", "skills": normalized}

@app.get("/users/{email}/skill-gap")
async def skill_gap(email: str, role: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: raise HTTPException(404, "User not found")
    
    user_skills = [s.lower() for s in user.get("skills", [])]
    role_skills = {
        "Data Scientist": ["python", "machine learning", "statistics", "pandas", "numpy", "deep learning", "matplotlib", "scikit-learn"],
        "Web Developer": ["html", "css", "javascript", "react", "node.js", "rest api", "frontend", "backend"],
        "ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"]
    }
    
    required = role_skills.get(role, [])
    existing = [s for s in required if s.lower() in user_skills]
    missing = [s for s in required if s.lower() not in user_skills]
    
    return {"role": role, "required_skills": required, "existing_skills": existing, "missing_skills": missing}

@app.get("/search")
async def search(q: str = ""):
    if not q: return {"results": []}
    cursor = db.courses.find({"title": {"$regex": q.strip(), "$options": "i"}})
    results = await cursor.to_list(10)
    for c in results: c["_id"] = str(c["_id"])
    return {"results": results}

# ---------------- LEARNING PATH & ACTIVITY ----------------

@app.post("/users/{email}/add-course")
async def add_course(email: str, course: AddCourseIn):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user: raise HTTPException(404, "User not found")
    
    daily = float(user.get("available_hours_per_day", 1))
    total_days = ceil(float(course.hours) / daily)
    roadmap = [
        {"step": 1, "task": "Foundations", "duration": f"{ceil(total_days*0.2)} days"},
        {"step": 2, "task": "Core Learning", "duration": f"{ceil(total_days*0.5)} days"},
        {"step": 3, "task": "Final Project", "duration": f"{ceil(total_days*0.3)} days"},
    ]
    
    new_course = {**course.dict(), "days_to_complete": total_days, "roadmap": roadmap, "added_at": datetime.utcnow()}
    await db.users.update_one({"email": email}, {"$push": {"learning_path": new_course}})
    await award_badge(email, "Course Explorer")
    return {"msg": "ok", "course": new_course}

@app.get("/users/{email}/activity")
async def activity(email: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: return {"streak": 0, "learning_path": []}
    return {"streak": user.get("streak", 0), "learning_path": user.get("learning_path", [])}

@app.get("/users/{email}/badges")
async def get_badges(email: str):
    cursor = db.user_badges.find({"email": email.lower().strip()})
    badges = await cursor.to_list(100)
    for b in badges: b["_id"] = str(b["_id"])
    return {"badges": badges}

# ---------------- QUIZ SYSTEM ----------------

@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    for q in quiz["questions"]: q.pop("answer", None)
    quiz["_id"] = str(quiz["_id"])
    return quiz

"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id, quiz_num = payload["course_id"], int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / len(quiz["questions"])) * 100
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, "total": len(quiz["questions"]), 
        "percentage": percent, "answers": answers, "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    if percent >= 80: await award_badge(email, f"Level {quiz_num} Master")
    return {"score": correct_count, "total": len(quiz["questions"]), "percentage": round(percent, 2), "passed": percent >= 80, "details": details}"""

@app.get("/quiz/status")
async def get_quiz_status(email: str, course_id: str, quiz_num: int):
    email = email.lower().strip()
    result = await db.quiz_results.find_one({"email": email, "course_id": course_id, "quiz_number": quiz_num})
    if not result: return {"completed": False}
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: return {"completed": False}
    
    details = []
    user_answers = result.get("answers", [])
    for i, q in enumerate(quiz["questions"]):
        user_ans = user_answers[i] if i < len(user_answers) else -1
        details.append({"question": q["question"], "options": q["options"], "user_answer": user_ans, "correct_answer": q["answer"], "is_correct": user_ans == q["answer"]})
    
    return {"completed": True, "previous_result": {"score": result["score"], "total": result["total"], "percentage": result["percentage"], "passed": result["percentage"] >= 80, "details": details}}
"""@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if user already finished this
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    # If they already passed/completed, we send the answers back for the review screen
    result_data = None
    if prev_result:
        result_data = {
            "percentage": prev_result["percentage"],
            "passed": prev_result["percentage"] >= 60,
            "answers": prev_result["answers"]
        }

    return {
        "course_title": quiz.get("course_title", "Roadmap Level"),
        "questions": quiz["questions"],
        "previous_result": result_data
    }
@app.get("/users/{email}/quiz-results")
async def get_all_quiz_results(email: str):
    cursor = db.quiz_results.find({"email": email.lower().strip()})
    results = await cursor.to_list(length=100)
    final_list = []
    for res in results:
        # Find course title based on the course_id stored in the result
        course = await db.courses.find_one({"id": res.get("course_id")})
        
        final_list.append({
            "course_title": course["title"] if course else res.get("course_id", "Unknown Course"),
            "quiz_number": res.get("quiz_number", 1),
            "score": res.get("score", 0),      
            "total": res.get("total", 10),     
            "percentage": res.get("percentage", 0), 
            "completed_at": res.get("completed_at")
        })
    return final_list"""
"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id, quiz_num = payload["course_id"], int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    total_q = len(quiz["questions"])

    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / total_q) * 100
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, 
        "total": total_q, # Saving total dynamically
        "percentage": percent, 
        "answers": answers, 
        "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    if percent >= 80: await award_badge(email, f"Level {quiz_num} Master")
    return {"score": correct_count, "total": total_q, "percentage": round(percent, 2), "passed": percent >= 80, "details": details}
"""
"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id = payload["course_id"] # This will be "roadmap" for Know More
    quiz_num = int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    total_q = len(quiz["questions"])

    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / total_q) * 100
    
    # --- SPECIFIC ROADMAP LOGIC ---
    if course_id == "roadmap":
        pass_threshold = 60  # Lower threshold for Roadmap
        passed = percent >= pass_threshold
        
        new_max_level = None
        if passed:
            user = await db.users.find_one({"email": email})
            current_max = user.get("max_level", 1)
            # Only increment if they passed their current highest level
            if quiz_num >= current_max:
                new_max_level = quiz_num + 1
                await db.users.update_one({"email": email}, {"$set": {"max_level": new_max_level}})
    else:
        # Dashboard quizzes remain at 80%
        pass_threshold = 80
        passed = percent >= pass_threshold
        new_max_level = None

    # Save Result
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, "total": total_q, "percentage": percent, 
        "answers": answers, "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    return {
        "score": correct_count, 
        "total": total_q, 
        "percentage": round(percent, 2), 
        "passed": passed, 
        "details": details,
        "new_max_level": new_max_level
    }"""
# --- UPDATE THESE ROUTES IN main.py ---

"""@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Roadmap level not found")
    
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    # We must include 'answer' so the review screen works correctly
    questions = []
    for q in quiz["questions"]:
        questions.append({
            "question": q["question"], 
            "options": q["options"],
            "answer": q["answer"] 
        })

    return {
        "course_title": quiz.get("course_title", f"Level {level_num}"),
        "questions": questions,
        "previous_result": prev_result
    }"""
import json
import os
import csv
from math import ceil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# ---------------- CONFIG ----------------

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/course_reco")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

app = FastAPI(title="LMS Unified Backend - Production Ready")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class UserIn(BaseModel):
    email: str
    password: str
    available_hours_per_day: float = 1

class AddCourseIn(BaseModel):
    course_id: str
    title: str
    hours: float
    url: str = ""

# ---------------- UTILS ----------------

async def award_badge(email: str, badge_name: str):
    email = email.lower().strip()
    record = {
        "email": email,
        "badge_name": badge_name,
        "name": badge_name,
        "awarded_at": datetime.utcnow()
    }
    await db.user_badges.update_one(
        {"email": email, "badge_name": badge_name},
        {"$set": record},
        upsert=True
    )

# ---------------- STARTUP SEED ----------------

"""@app.on_event("startup")
async def startup_event():
    # 1. Setup Indexes
    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index([("course_id", 1), ("quiz_number", 1)], unique=True)
    await db.courses.create_index("id", unique=True)
    await db.quiz_results.create_index([("email", 1), ("course_id", 1), ("quiz_number", 1)], unique=True)

    # 2. Path Resolution
    current_file = os.path.abspath(__file__) 
    app_dir = os.path.dirname(current_file)
    backend_dir = os.path.dirname(app_dir)
    data_dir = os.path.join(backend_dir, "data")

    # 3. CRITICAL: Clear old quizzes for a fresh sync of 10-question levels
    await db.quizzes.delete_many({})
    print("🧹 Database cleared for fresh 10-question sync")

    # -------- Load Quizzes --------
   # -------- Load Quizzes with Error Handling --------
    quiz_path = os.path.join(data_dir, "quizzes.json")
    if os.path.exists(quiz_path):
        try:
            with open(quiz_path, "r") as f:
                quizzes = json.load(f)
                count = 0
                for q in quizzes:
                    # Ensure quiz_number is an integer for indexing
                    q["quiz_number"] = int(q["quiz_number"])
                    await db.quizzes.update_one(
                        {"course_id": q["course_id"], "quiz_number": q["quiz_number"]},
                        {"$set": q},
                        upsert=True
                    )
                    count += 1
                print(f"🚀 SUCCESS: Loaded {count} quiz levels from {quiz_path}")
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: quizzes.json has a syntax error: {e}")
        except Exception as e:
            print(f"❌ ERROR: Failed to load quizzes: {e}")

    # -------- Load Courses --------
    csv_path = os.path.join(data_dir, "seed.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                course_id = row.get("id") or row.get("course_id")
                if not course_id: continue
                row["duration_hours"] = float(row.get("duration_hours", 1))
                row["price"] = float(row.get("price", 0))
                await db.courses.update_one({"id": course_id}, {"$set": row}, upsert=True)
            print(f"✅ Courses seeded from {csv_path}")"""
@app.on_event("startup")
async def startup_event():
    # 1. Setup Indexes
    await db.users.create_index("email", unique=True)
    await db.quizzes.create_index([("course_id", 1), ("quiz_number", 1)], unique=True)
    
    # 2. Path Resolution: Go UP from backend to find data
    # os.path.abspath(__file__) -> /project/backend/main.py
    # dirname -> /project/backend
    # dirname again -> /project (the parent folder)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    data_dir = os.path.join(project_root, "data")
    
    print(f"🔍 Searching for data in: {data_dir}")

    # 3. Fresh Sync
    await db.quizzes.delete_many({})

    async def load_json(filename, is_roadmap=False):
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for q in data:
                        c_id = "roadmap" if is_roadmap else q["course_id"]
                        q["quiz_number"] = int(q["quiz_number"])
                        await db.quizzes.update_one(
                            {"course_id": c_id, "quiz_number": q["quiz_number"]},
                            {"$set": q},
                            upsert=True
                        )
                print(f"🚀 SUCCESS: Loaded {len(data)} items from {filename}")
            except Exception as e:
                print(f"❌ JSON ERROR in {filename}: {e}")
        else:
            print(f"⚠️ FILE NOT FOUND: {path}")

    # Load both files from the folder outside 'backend'
    await load_json("quizzes.json", is_roadmap=False)
    await load_json("roadmap_quizzes.json", is_roadmap=True)

# ---------------- AUTH & USERS ----------------

@app.post("/auth/register")
async def register(u: UserIn):
    email = u.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing: raise HTTPException(400, "Email already registered")
    user_data = u.dict()
    user_data.update({"email": email, "streak": 1, "learning_path": [], "skills": []})
    await db.users.insert_one(user_data)
    return {"msg": "ok"}

@app.post("/auth/login")
async def login(u: UserIn):
    user = await db.users.find_one({"email": u.email.lower().strip()})
    if not user or user["password"] != u.password:
        raise HTTPException(401, "Invalid credentials")
    return {"msg": "ok", "user": {"email": user["email"], "available_hours_per_day": user.get("available_hours_per_day", 1)}}

@app.get("/users/{email}")
async def get_user(email: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: raise HTTPException(404, "User not found")
    user["_id"] = str(user["_id"])
    return user

# ---------------- SKILLS & SEARCH ----------------

@app.put("/users/{email}/skills")
async def update_skills(email: str, skills: list = Body(...)):
    email = email.lower().strip()
    normalized = list({s.strip().lower() for s in skills if s.strip()})
    await db.users.update_one({"email": email}, {"$set": {"skills": normalized}})
    return {"msg": "skills updated", "skills": normalized}

@app.get("/users/{email}/skill-gap")
async def skill_gap(email: str, role: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: raise HTTPException(404, "User not found")
    
    user_skills = [s.lower() for s in user.get("skills", [])]
    role_skills = {
        "Data Scientist": ["python", "machine learning", "statistics", "pandas", "numpy", "deep learning", "matplotlib", "scikit-learn"],
        "Web Developer": ["html", "css", "javascript", "react", "node.js", "rest api", "frontend", "backend"],
        "ML Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"]
    }
    
    required = role_skills.get(role, [])
    existing = [s for s in required if s.lower() in user_skills]
    missing = [s for s in required if s.lower() not in user_skills]
    
    return {"role": role, "required_skills": required, "existing_skills": existing, "missing_skills": missing}

@app.get("/search")
async def search(q: str = ""):
    if not q: return {"results": []}
    cursor = db.courses.find({"title": {"$regex": q.strip(), "$options": "i"}})
    results = await cursor.to_list(10)
    for c in results: c["_id"] = str(c["_id"])
    return {"results": results}

# ---------------- LEARNING PATH & ACTIVITY ----------------

@app.post("/users/{email}/add-course")
async def add_course(email: str, course: AddCourseIn):
    email = email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user: raise HTTPException(404, "User not found")
    
    daily = float(user.get("available_hours_per_day", 1))
    total_days = ceil(float(course.hours) / daily)
    roadmap = [
        {"step": 1, "task": "Foundations", "duration": f"{ceil(total_days*0.2)} days"},
        {"step": 2, "task": "Core Learning", "duration": f"{ceil(total_days*0.5)} days"},
        {"step": 3, "task": "Final Project", "duration": f"{ceil(total_days*0.3)} days"},
    ]
    
    new_course = {**course.dict(), "days_to_complete": total_days, "roadmap": roadmap, "added_at": datetime.utcnow()}
    await db.users.update_one({"email": email}, {"$push": {"learning_path": new_course}})
    await award_badge(email, "Course Explorer")
    return {"msg": "ok", "course": new_course}

@app.get("/users/{email}/activity")
async def activity(email: str):
    user = await db.users.find_one({"email": email.lower().strip()})
    if not user: return {"streak": 0, "learning_path": []}
    return {"streak": user.get("streak", 0), "learning_path": user.get("learning_path", [])}

@app.get("/users/{email}/badges")
async def get_badges(email: str):
    cursor = db.user_badges.find({"email": email.lower().strip()})
    badges = await cursor.to_list(100)
    for b in badges: b["_id"] = str(b["_id"])
    return {"badges": badges}

# ---------------- QUIZ SYSTEM ----------------

@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    for q in quiz["questions"]: q.pop("answer", None)
    quiz["_id"] = str(quiz["_id"])
    return quiz

"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id, quiz_num = payload["course_id"], int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / len(quiz["questions"])) * 100
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, "total": len(quiz["questions"]), 
        "percentage": percent, "answers": answers, "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    if percent >= 80: await award_badge(email, f"Level {quiz_num} Master")
    return {"score": correct_count, "total": len(quiz["questions"]), "percentage": round(percent, 2), "passed": percent >= 80, "details": details}"""

@app.get("/quiz/status")
async def get_quiz_status(email: str, course_id: str, quiz_num: int):
    email = email.lower().strip()
    result = await db.quiz_results.find_one({"email": email, "course_id": course_id, "quiz_number": quiz_num})
    if not result: return {"completed": False}
    
    # Threshold logic: 40% for roadmap, 80% for everything else
    threshold = 40 if course_id == "roadmap" else 65
    passed = result.get("percentage", 0) >= threshold
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    details = []
    user_answers = result.get("answers", [])
    
    if quiz:
        for i, q in enumerate(quiz["questions"]):
            user_ans = user_answers[i] if i < len(user_answers) else -1
            details.append({
                "question": q["question"], 
                "options": q["options"], 
                "user_answer": user_ans, 
                "correct_answer": q["answer"], 
                "is_correct": user_ans == q["answer"]
            })
    
    return {
        "completed": True, 
        "previous_result": {
            "score": result.get("score", 0), 
            "total": result.get("total", 0), 
            "percentage": result.get("percentage", 0), 
            "passed": passed, 
            "details": details
        }
    }
"""@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if user already finished this
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    # If they already passed/completed, we send the answers back for the review screen
    result_data = None
    if prev_result:
        result_data = {
            "percentage": prev_result["percentage"],
            "passed": prev_result["percentage"] >= 60,
            "answers": prev_result["answers"]
        }

    return {
        "course_title": quiz.get("course_title", "Roadmap Level"),
        "questions": quiz["questions"],
        "previous_result": result_data
    }
@app.get("/users/{email}/quiz-results")
async def get_all_quiz_results(email: str):
    cursor = db.quiz_results.find({"email": email.lower().strip()})
    results = await cursor.to_list(length=100)
    final_list = []
    for res in results:
        # Find course title based on the course_id stored in the result
        course = await db.courses.find_one({"id": res.get("course_id")})
        
        final_list.append({
            "course_title": course["title"] if course else res.get("course_id", "Unknown Course"),
            "quiz_number": res.get("quiz_number", 1),
            "score": res.get("score", 0),      
            "total": res.get("total", 10),     
            "percentage": res.get("percentage", 0), 
            "completed_at": res.get("completed_at")
        })
    return final_list"""
"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id, quiz_num = payload["course_id"], int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    total_q = len(quiz["questions"])

    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / total_q) * 100
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, 
        "total": total_q, # Saving total dynamically
        "percentage": percent, 
        "answers": answers, 
        "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    if percent >= 80: await award_badge(email, f"Level {quiz_num} Master")
    return {"score": correct_count, "total": total_q, "percentage": round(percent, 2), "passed": percent >= 80, "details": details}
"""
"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id = payload["course_id"] # This will be "roadmap" for Know More
    quiz_num = int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count, details = 0, []
    total_q = len(quiz["questions"])

    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], 
            "options": q["options"], 
            "user_answer": user_ans, 
            "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / total_q) * 100
    
    # --- SPECIFIC ROADMAP LOGIC ---
    if course_id == "roadmap":
        pass_threshold = 60  # Lower threshold for Roadmap
        passed = percent >= pass_threshold
        
        new_max_level = None
        if passed:
            user = await db.users.find_one({"email": email})
            current_max = user.get("max_level", 1)
            # Only increment if they passed their current highest level
            if quiz_num >= current_max:
                new_max_level = quiz_num + 1
                await db.users.update_one({"email": email}, {"$set": {"max_level": new_max_level}})
    else:
        # Dashboard quizzes remain at 80%
        pass_threshold = 80
        passed = percent >= pass_threshold
        new_max_level = None

    # Save Result
    result_entry = {
        "email": email, "course_id": course_id, "quiz_number": quiz_num, 
        "score": correct_count, "total": total_q, "percentage": percent, 
        "answers": answers, "completed_at": datetime.utcnow()
    }
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": result_entry}, upsert=True
    )
    
    return {
        "score": correct_count, 
        "total": total_q, 
        "percentage": round(percent, 2), 
        "passed": passed, 
        "details": details,
        "new_max_level": new_max_level
    }"""
# --- UPDATE THESE ROUTES IN main.py ---

"""@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Roadmap level not found")
    
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    # We must include 'answer' so the review screen works correctly
    questions = []
    for q in quiz["questions"]:
        questions.append({
            "question": q["question"], 
            "options": q["options"],
            "answer": q["answer"] 
        })

    return {
        "course_title": quiz.get("course_title", f"Level {level_num}"),
        "questions": questions,
        "previous_result": prev_result
    }"""
# 1. PLACE THIS ABOVE THE GENERIC /quiz/{course_id} ROUTE
"""@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    # Return questions WITH answers for the review screen
    questions_data = []
    for q in quiz.get("questions", []):
        questions_data.append({
            "question": q.get("question"),
            "options": q.get("options"),
            "answer": q.get("answer") 
        })

    return {
        "course_title": quiz.get("course_title"),
        "questions": questions_data,
        "previous_result": prev_result
    }
"""
@app.get("/quiz/{course_id}/{quiz_num}")
async def get_quiz(course_id: str, quiz_num: int):
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(status_code=404, detail="Quiz not found")
    
    # IMPORTANT: DO NOT q.pop("answer") here. 
    # The Frontend review logic needs 'answer' to compare with 'user_answer'.
    
    quiz["_id"] = str(quiz["_id"])
    return quiz
# 2. UPDATE YOUR SUBMISSION TO ACTUALLY UNLOCK LEVELS
"""@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id = payload["course_id"]
    quiz_num = int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    
    # Calculate score...
    correct = sum(1 for i, q in enumerate(quiz["questions"]) if i < len(answers) and answers[i] == q["answer"])
    percent = (correct / len(quiz["questions"])) * 100
    passed = percent >= 40

    # Save Result
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": {"percentage": percent, "passed": passed, "answers": answers}}, 
        upsert=True
    )

    # UNLOCK NEXT LEVEL
    if passed and course_id == "roadmap":
        user = await db.users.find_one({"email": email})
        if quiz_num >= user.get("max_level", 1):
            await db.users.update_one({"email": email}, {"$set": {"max_level": quiz_num + 1}})

    return {"percentage": percent, "passed": passed}"""
@app.post("/quiz/submit")
async def submit_quiz(payload: dict = Body(...)):
    email = payload["email"].lower().strip()
    course_id = payload["course_id"]
    quiz_num = int(payload["quiz_number"])
    answers = payload.get("answers", [])
    
    quiz = await db.quizzes.find_one({"course_id": course_id, "quiz_number": quiz_num})
    if not quiz: raise HTTPException(404, "Quiz not found")

    correct_count = 0
    total_q = len(quiz["questions"])
    details = []

    for i, q in enumerate(quiz["questions"]):
        user_ans = answers[i] if i < len(answers) else -1
        is_correct = (user_ans == q["answer"])
        if is_correct: correct_count += 1
        details.append({
            "question": q["question"], "options": q["options"], 
            "user_answer": user_ans, "correct_answer": q["answer"], 
            "is_correct": is_correct
        })

    percent = (correct_count / total_q) * 100
    
    # --- CONSISTENT THRESHOLDS ---
    # Know More (Roadmap) = 40%, Dashboard Quizzes = 65%
    pass_threshold = 40 if course_id == "roadmap" else 65
    passed = percent >= pass_threshold

    new_max_level = None
    if passed and course_id == "roadmap":
        user = await db.users.find_one({"email": email})
        current_max = user.get("max_level", 1)
        if quiz_num >= current_max:
            new_max_level = quiz_num + 1
            await db.users.update_one({"email": email}, {"$set": {"max_level": new_max_level}})

    # Save Result
    await db.quiz_results.update_one(
        {"email": email, "course_id": course_id, "quiz_number": quiz_num},
        {"$set": {
            "score": correct_count, "total": total_q, "percentage": percent,
            "passed": passed, "answers": answers, "completed_at": datetime.utcnow()
        }}, upsert=True
    )

    return {
        "score": correct_count, "total": total_q, "percentage": round(percent, 2),
        "passed": passed, "details": details, "new_max_level": new_max_level
    }

# --- GET HISTORY ENDPOINT ---
@app.get("/users/{email}/quiz-results")
async def get_all_quiz_results(email: str):
    email_clean = email.lower().strip()
    cursor = db.quiz_results.find({"email": email_clean})
    results = await cursor.to_list(length=100)
    
    final_list = []
    for res in results:
        course_id = res.get("course_id")
        percentage = res.get("percentage", 0)
        
        # Determine the threshold based on the course type
        if course_id == "roadmap":
            threshold = 40  
            course_title = "Roadmap Journey"
        else:
            threshold = 65  
            course = await db.courses.find_one({"id": course_id})
            course_title = course["title"] if course else course_id
        
        # Calculate status based on specific threshold
        is_passed = percentage >= threshold

        final_list.append({
            "course_title": course_title,
            "quiz_number": res.get("quiz_number", 1),
            "score": res.get("score", 0),      
            "total": res.get("total", 0),     
            "percentage": round(percentage, 1), 
            "passed": is_passed, # This boolean is now sent to frontend
            "completed_at": res.get("completed_at").strftime("%Y-%m-%d") if res.get("completed_at") else "N/A"
        })
    
    return final_list[::-1] # Reverse to show newest first
@app.get("/quiz/roadmap/{level_num}")
async def get_roadmap_quiz(level_num: int, email: str = None):
    """Specific route for the Know More / Roadmap levels"""
    quiz = await db.quizzes.find_one({"course_id": "roadmap", "quiz_number": level_num})
    if not quiz:
        raise HTTPException(404, "Roadmap level not found")
    
    prev_result = None
    if email:
        prev_result = await db.quiz_results.find_one({
            "email": email.lower().strip(), 
            "course_id": "roadmap", 
            "quiz_number": level_num
        })

    return {
        "course_title": quiz.get("course_title", f"Level {level_num}"),
        "questions": quiz["questions"], # Answers are included for review
        "previous_result": prev_result
    }