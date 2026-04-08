import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

export default function CourseDetails({ user }) {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    async function fetchCourse() {
      const res = await axios.get("http://127.0.0.1:8000/courses?limit=100");
      const found = res.data.courses.find(c => c.id === courseId);
      setCourse(found);
    }
    fetchCourse();
  }, [courseId]);

  const addCourse = async () => {
    try {
      if (!user || !course) return;
      await axios.post(`http://127.0.0.1:8000/users/${user.email}/add-course`, {
        course_id: course.id,
        title: course.title,
        hours: course.duration_hours || 1,
      });
      setAdded(true);
      alert(`Added course! Estimated days: ${Math.ceil(course.duration_hours / user.available_hours_per_day)}`);
    }
    catch {
      alert("Error adding course");
    }
  };

  if (!course) return <div>Loading...</div>;

  return (
    <div>
      <h2>{course.title}</h2>
      <p>Provider: {course.provider}</p>
      <p>Duration: {course.duration_hours} hours</p>
      <button onClick={addCourse} disabled={added}>
        {added ? "Added to Path" : "Add to Learning Path"}
      </button>
    </div>
  );
}
