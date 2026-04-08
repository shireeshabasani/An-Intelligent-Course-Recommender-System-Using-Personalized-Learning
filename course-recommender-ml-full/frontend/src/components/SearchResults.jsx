import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export default function SearchResults() {
  const [params] = useSearchParams();
  const query = params.get("q") || "";
  const [results, setResults] = useState([]);
  const [platform, setPlatform] = useState("All");
  const [price, setPrice] = useState("All");
  const [level, setLevel] = useState("All");

  useEffect(() => {
    if (query) {
      const mockResults = [
        {
          id: 1,
          title: `Mastering ${query} with Real Projects`,
          provider: "Coursera",
          rating: 4.8,
          duration_hours: 14,
          price: "Free",
          level: "Beginner",
          image: "https://images.unsplash.com/photo-1581094651181-3592a2078584?auto=format&fit=crop&w=800&q=80", // team/project/office
          url: "https://www.coursera.org/search?query=data",
        },
        {
          id: 2,
          title: `Learn ${query} from Scratch`,
          provider: "YouTube",
          rating: 4.7,
          duration_hours: 8,
          price: "Free",
          level: "Beginner",
          image: "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=800&q=80", // books/self study
          url: "https://www.youtube.com/results?search_query=data",
        },
        {
          id: 3,
          title: "Data Fundamentals",
          provider: "edX",
          rating: 4.5,
          duration_hours: 12,
          price: "Free",
          level: "Advanced",
          image: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80", // data
          url: "https://www.edx.org/search?q=data",
        },
        {
          id: 4,
          title: `Advanced ${query} Techniques`,
          provider: "Skillshare",
          rating: 4.4,
          duration_hours: 9,
          price: "Premium (Free Trial)",
          level: "Intermediate",
          image: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80", // advanced workspace
          url: "https://www.skillshare.com/en/search?query=data",
        },
        {
          id: 5,
          title: `${query} Made Simple`,
          provider: "Khan Academy",
          rating: 4.9,
          duration_hours: 7,
          price: "Free",
          level: "Beginner",
          image: "https://images.unsplash.com/photo-1472289065668-ce650ac443d2?auto=format&fit=crop&w=800&q=80", // simple learning
          url: "https://www.khanacademy.org/search?search_again=1&page_search_query=data",
        },
        {
          id: 6,
          title: "Data Science and Machine Learning Bootcamp",
          provider: "edX",
          rating: 4.8,
          duration_hours: 40,
          price: "Free",
          level: "Advanced",
          image: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80", // code/data science
          url: "https://www.edx.org/course/data-science-bootcamp",
        },
        {
          id: 7,
          title: "Cybersecurity Fundamentals",
          provider: "LinkedIn Learning",
          rating: 4.6,
          duration_hours: 12,
          price: "₹1,400 / month (Free Trial)",
          level: "Beginner",
          image: "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=800&q=80", // cybersecurity/locks
          url: "https://www.linkedin.com/learning/cybersecurity-fundamentals",
        },
        {
          id: 8,
          title: "Mobile Apps with Flutter & Dart",
          provider: "Udemy",
          rating: 4.5,
          duration_hours: 22,
          price: "₹799",
          level: "Intermediate",
          image: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80", // mobile apps
          url: "https://www.udemy.com/course/flutter-dart",
        },
        {
          id: 9,
          title: "Advanced SQL for Data Analysis",
          provider: "FutureLearn",
          rating: 4.7,
          duration_hours: 18,
          price: "Free Access / Upgrade ₹1,600",
          level: "Advanced",
          image: "https://images.unsplash.com/photo-1466781783364-36c955e42a02?auto=format&fit=crop&w=800&q=80", // sql/database
          url: "https://www.futurelearn.com/courses/advanced-sql",
        }
      ];
      setTimeout(() => {
        setResults(mockResults);
      }, 600);
    }
  }, [query]);

  const filteredResults = results.filter(r => {
    const matchesPlatform = platform === "All" || r.provider === platform;
    const p = r.price.toLowerCase();
    const isFree = p.includes("free") || p.includes("free trial");
    const isPaid = !isFree;
    const matchesPrice = price === "All" || (price === "Free" && isFree) || (price === "Paid" && isPaid);
    const matchesLevel = level === "All" || (r.level && r.level.toLowerCase() === level.toLowerCase());
    return matchesPlatform && matchesPrice && matchesLevel;
  });

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif", backgroundColor: "#f7f9fc", minHeight: "100vh" }}>
      <h2 style={{ textAlign: "center", color: "#333", marginBottom: "30px" }}>
        Search Results for "<span style={{ color: "#ff6600" }}>{query}</span>"
      </h2>
      
      <div style={{ marginBottom: 25, display: 'flex', gap: 20, alignItems: 'center', justifyContent: 'center' }}>
        <div>
          <label style={{ fontWeight: 'bold', marginRight: 10 }}>Platform:</label>
          <select value={platform} onChange={e => setPlatform(e.target.value)}>
            <option>All</option>
            <option>Coursera</option>
            <option>Udemy</option>
            <option>YouTube</option>
            <option>edX</option>
            <option>Skillshare</option>
            <option>Khan Academy</option>
            <option>LinkedIn Learning</option>
            <option>FutureLearn</option>
          </select>
        </div>
        <div>
          <label style={{ fontWeight: 'bold', marginRight: 10 }}>Price:</label>
          <select value={price} onChange={e => setPrice(e.target.value)}>
            <option>All</option>
            <option>Free</option>
            <option>Paid</option>
          </select>
        </div>
        <div>
          <label style={{ fontWeight: 'bold', marginRight: 10 }}>Level:</label>
          <select value={level} onChange={e => setLevel(e.target.value)}>
            <option>All</option>
            <option>Beginner</option>
            <option>Intermediate</option>
            <option>Advanced</option>
          </select>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "25px" }}>
        {filteredResults.length === 0 && <p>No courses found.</p>}
        {filteredResults.map((r) => (
          <div
            key={r.id}
            style={{
              backgroundColor: "#fff",
              borderRadius: "15px",
              boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
              overflow: "hidden",
              transition: "transform 0.3s, box-shadow 0.3s",
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = "scale(1.02)";
              e.currentTarget.style.boxShadow = "0 6px 15px rgba(0,0,0,0.2)";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = "scale(1)";
              e.currentTarget.style.boxShadow = "0 4px 10px rgba(0,0,0,0.1)";
            }}
          >
            <img
              src={r.image}
              alt={r.title}
              style={{ width: "100%", height: "180px", objectFit: "cover" }}
              onError={e => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/300x180.png?text=Course+Image";
              }}
            />
            <div style={{ padding: "15px" }}>
              <h3 style={{ fontSize: "1.2rem", color: "#333", marginBottom: "8px" }}>{r.title}</h3>
              <p style={{ color: "#666", marginBottom: "6px" }}><strong>Platform:</strong> {r.provider}</p>
              <p style={{ color: "#666", marginBottom: "6px" }}><strong>Duration:</strong> {r.duration_hours} hrs</p>
              <p style={{ color: "#666", marginBottom: "6px" }}><strong>Price:</strong> {r.price}</p>
              <p style={{ color: "#ffb400", marginBottom: "12px" }}>⭐ {r.rating} / 5</p>
              <p style={{ color: "#666", marginBottom: "6px" }}><strong>Level:</strong> {r.level || "N/A"}</p>
              <a
                href={r.url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: "inline-block",
                  padding: "10px 18px",
                  backgroundColor: "#ff6600",
                  color: "#fff",
                  borderRadius: "8px",
                  textDecoration: "none",
                  fontWeight: "bold",
                }}
              >
                Open Course
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
