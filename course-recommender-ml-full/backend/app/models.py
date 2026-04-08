from pydantic import BaseModel

class CourseIn(BaseModel):
    provider: str
    id: str
    title: str
    description: str = ""
    price: float = None
    duration_hours: float = None
    level: str = "Beginner"
    tags: list = []
    url: str = ""
