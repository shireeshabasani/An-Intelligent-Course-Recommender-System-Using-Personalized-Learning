import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Dashboard = ({ user }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [learningPath, setLearningPath] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchActivity() {
      if (!user) return;
      try {
        const res = await axios.get(`http://127.0.0.1:8000/users/${encodeURIComponent(user.email)}/activity`);
        const pathWithIds = (res.data.learning_path || []).map(c => ({
          ...c,
          validId: c.course_id || c.id || c._id
        }));
        setLearningPath(pathWithIds);
      } catch (err) {
        setLearningPath([]);
      }
    }
    fetchActivity();
  }, [user]);

  const handleSearch = async () => {
    if (!query) return;
    try {
      const res = await axios.get(`http://127.0.0.1:8000/search?q=${query}`);
      setResults(res.data.results.map(c => ({ ...c, id: c.id || c._id })));
    } catch (err) {
      console.error("Search failed", err);
    }
  };

  const handleSelectCourse = async (course) => {
    try {
      const response = await axios.post(`http://127.0.0.1:8000/users/${encodeURIComponent(user.email)}/add-course`, {
        course_id: course.id,
        title: course.title,
        hours: course.duration_hours || 1,
        url: course.url,
      });
      alert("Course and Roadmap generated!");
      
      const newCourse = {
        ...response.data.course,
        validId: response.data.course.course_id || response.data.course.id
      };
      
      setLearningPath((prev) => [...prev, newCourse]);
    } catch (err) { 
      alert("Failed to add course"); 
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto", fontFamily: "sans-serif", backgroundColor: "#f9fafb", minHeight: "100vh" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" }}>
        <h1>Welcome, {user?.email?.split('@')[0]}! 👋</h1>
        {/* Achievements button removed from here */}
      </header>

      {/* Final Exam Section */}
      <div style={{ background: "linear-gradient(135deg, #1e3a8a, #3b82f6)", color: "white", padding: "30px", borderRadius: "15px", marginBottom: "40px", textAlign: "center", boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)" }}>
        <h2 style={{ margin: "0 0 10px 0" }}>🎓 Ready for Graduation?</h2>
        <p>Complete the Final Syllabus Exam to earn your Professional Certification.</p>
        <button onClick={() => navigate("/quiz/final-exam/1")} style={{ padding: "12px 25px", fontSize: "16px", fontWeight: "bold", backgroundColor: "#fbbf24", color: "#1e3a8a", border: "none", borderRadius: "30px", cursor: "pointer", marginTop: "10px" }}>
          Start Final Syllabus Quiz
        </button>
      </div>

      {/* Learning Path Section */}
      <section>
        <h2 style={{ marginBottom: "20px" }}>Your Learning Path & Roadmap</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))", gap: "25px" }}>
          {learningPath.length === 0 ? (
            <p style={{ color: "#666" }}>No courses added yet. Start searching below!</p>
          ) : (
            learningPath.map((course, idx) => (
              <div key={idx} style={{ border: "1px solid #e5e7eb", borderRadius: "16px", backgroundColor: "#fff", boxShadow: "0 4px 6px rgba(0,0,0,0.05)", overflow: "hidden" }}>
                <div style={{ padding: "20px" }}>
                  <h3 style={{ marginTop: 0, color: "#111827" }}>{course.title}</h3>
                  
                  <div style={{ backgroundColor: "#f3f4f6", padding: "15px", borderRadius: "10px", margin: "15px 0" }}>
                    <p style={{ fontSize: "12px", fontWeight: "bold", color: "#4b5563", marginBottom: "10px", textTransform: "uppercase" }}>📍 Your Study Roadmap</p>
                    {course.roadmap && course.roadmap.length > 0 ? (
                      course.roadmap.map((step, sIdx) => (
                        <div key={sIdx} style={{ display: "flex", alignItems: "flex-start", gap: "10px", marginBottom: "8px" }}>
                          <div style={{ minWidth: "20px", height: "20px", borderRadius: "50%", backgroundColor: "#3b82f6", color: "white", fontSize: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>{sIdx + 1}</div>
                          <div>
                            <p style={{ fontSize: "13px", margin: 0, fontWeight: "500" }}>{step.task}</p>
                            <p style={{ fontSize: "11px", color: "#6b7280", margin: 0 }}>Duration: {step.duration}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p style={{ fontSize: "12px", color: "#9ca3af" }}>Roadmap generating...</p>
                    )}
                  </div>

                  <button onClick={() => window.open(course.url, "_blank")} style={{ width: "100%", padding: "10px", marginBottom: "15px", borderRadius: "8px", border: "1px solid #3b82f6", backgroundColor: "white", color: "#3b82f6", cursor: "pointer", fontWeight: "bold" }}>
                    View Learning Material 📖
                  </button>

                  <div style={{ borderTop: "1px solid #f3f4f6", paddingTop: "15px" }}>
                    <p style={{ fontSize: "13px", color: "#374151", marginBottom: "10px", fontWeight: "bold" }}>Level Progress (Quizzes):</p>
                    <div style={{ display: "flex", gap: "8px" }}>
                      {[1, 2, 3, 4, 5].map((num) => (
                        <button 
                          key={num} 
                          onClick={() => {
                            if (course.validId) {
                              navigate(`/quiz/${course.validId}/${num}`);
                            } else {
                              alert("Error: Course ID not found.");
                            }
                          }} 
                          style={{ flex: 1, padding: "8px 0", borderRadius: "6px", border: "none", backgroundColor: "#10b981", color: "white", cursor: "pointer", fontSize: "11px", fontWeight: "bold" }}
                        >
                          Lvl {num}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Search Section */}
      <section style={{ marginTop: "60px", paddingBottom: "40px" }}>
        <h2 style={{ marginBottom: "20px" }}>Explore New Courses</h2>
        <div style={{ display: "flex", gap: "10px", marginBottom: "25px" }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search (e.g., Python, Machine Learning)..." style={{ flex: 1, padding: "14px", borderRadius: "10px", border: "1px solid #d1d5db", fontSize: "16px" }} />
          <button onClick={handleSearch} style={{ padding: "0 30px", backgroundColor: "#111827", color: "white", border: "none", borderRadius: "10px", cursor: "pointer", fontWeight: "bold" }}>Search</button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "15px" }}>
          {results.map((course) => (
            <div key={course.id} style={{ padding: "15px", border: "1px solid #e5e7eb", borderRadius: "12px", backgroundColor: "white", display: "flex", justifyContent: "space-between", alignItems: "center", boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ fontWeight: "600", color: "#111827" }}>{course.title}</span>
                <span style={{ fontSize: "12px", color: "#6b7280" }}>{course.duration_hours} Hours • {course.provider}</span>
              </div>
              <button onClick={() => handleSelectCourse(course)} style={{ padding: "8px 15px", backgroundColor: "#3b82f6", color: "white", border: "none", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>+ Add</button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;