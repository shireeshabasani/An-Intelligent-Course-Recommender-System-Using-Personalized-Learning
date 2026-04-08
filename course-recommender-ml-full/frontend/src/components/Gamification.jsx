import React from "react";
import { useNavigate } from "react-router-dom";

const Gamification = () => {
  const navigate = useNavigate();
  return (
    <div style={{ padding: "60px 20px", maxWidth: "1000px", margin: "0 auto", textAlign: "center" }}>
      <h1 style={{ fontSize: "32px", color: "#1e3a8a" }}>Gamification Center 🚀</h1>
      <p style={{ color: "#64748b", marginBottom: "40px", fontSize: "18px" }}>
        Transform your learning into an adventure. Earn XP, unlock badges, and master your field.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px" }}>
        <div style={questCard}>
          <div style={{ fontSize: "40px" }}>🛡️</div>
          <h3>Daily Challenge</h3>
          <p>Complete one 5-minute quiz to keep your 5-day streak alive!</p>
          <button style={btnPrimary} onClick={() => navigate("/quiz/ds-1/1")}>Start Quest</button>
        </div>
        <div style={questCard}>
          <div style={{ fontSize: "40px" }}>⚔️</div>
          <h3>Skill Duel</h3>
          <p>Test your Machine Learning knowledge against the Level 3 boss.</p>
          <button style={btnPrimary} onClick={() => navigate("/quiz/cour1/3")}>Battle Now</button>
        </div>
      </div>
    </div>
  );
};

const questCard = { padding: "30px", borderRadius: "20px", backgroundColor: "#fff", boxShadow: "0 4px 20px rgba(0,0,0,0.05)", border: "1px solid #f1f5f9" };
const btnPrimary = { marginTop: "15px", padding: "10px 25px", borderRadius: "8px", border: "none", backgroundColor: "#3b82f6", color: "#fff", fontWeight: "bold", cursor: "pointer" };
export default Gamification;
