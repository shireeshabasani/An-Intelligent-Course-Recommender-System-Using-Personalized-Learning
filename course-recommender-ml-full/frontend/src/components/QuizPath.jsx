import React from "react";

export default function QuizPath() {
  const levels = ["Lv 1", "Lv 2", "Lv 3", "Lv 4", "Lv 5", "Lv 6"];

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f8faff", fontFamily: "Arial" }}>
      {/* Blue Header Container */}
      <div style={{ backgroundColor: "#0056b3", color: "#fff", textAlign: "center", padding: "60px 20px" }}>
        <h1 style={{ fontSize: "2.8rem", marginBottom: "10px" }}>Congratulations 🎉</h1>
        
        {/* White Rating Circle */}
        <div style={scoreCircleStyle}>
          <div style={{ fontSize: "28px", fontWeight: "bold" }}>5/5</div>
          <div style={{ color: "#ffc107", fontSize: "18px" }}>★★★★★</div>
        </div>
        
        <h2 style={{ fontSize: "2rem", marginBottom: "5px" }}>Akhila ✅</h2>
        <p style={{ opacity: 0.9 }}>You are now a verified candidate.</p>
      </div>

      {/* Roadmap / Level Section */}
      <div style={{ padding: "50px 20px", textAlign: "center" }}>
        <div style={{ display: "flex", justifyContent: "center", gap: "40px", flexWrap: "wrap", maxWidth: "900px", margin: "0 auto" }}>
          {levels.map((lvl, index) => (
            <div key={index} style={{ textAlign: "center" }}>
              <div style={lockCircleStyle}>🔒</div>
              <div style={{ marginTop: "12px", color: "#555", fontSize: "14px" }}>{lvl}</div>
            </div>
          ))}
          
          {/* Final Master Level */}
          <div style={{ textAlign: "center" }}>
            <div style={{ ...lockCircleStyle, backgroundColor: "#007bff", color: "#fff", border: "none" }}>👑</div>
            <div style={{ marginTop: "12px", fontWeight: "bold", color: "#007bff" }}>Master Level</div>
          </div>
        </div>
      </div>
    </div>
  );
}

const scoreCircleStyle = {
  width: "120px",
  height: "120px",
  backgroundColor: "#fff",
  borderRadius: "50%",
  margin: "25px auto",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  color: "#000",
  border: "6px solid #ffc107",
  boxShadow: "0 5px 15px rgba(0,0,0,0.2)"
};

const lockCircleStyle = {
  width: "65px",
  height: "65px",
  borderRadius: "50%",
  border: "2px solid #ddd",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "22px",
  backgroundColor: "#fff",
  boxShadow: "0 2px 5px rgba(0,0,0,0.05)"
};