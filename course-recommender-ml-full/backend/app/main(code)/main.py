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

    return result
