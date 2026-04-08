import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Register({ onRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [availableHours, setAvailableHours] = useState(1);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!email || !password || !availableHours) {
      setMessage("Please fill all required fields!");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          available_hours_per_day: availableHours,
        }),
      });

      if (response.ok) {
        onRegister({ email, available_hours_per_day: availableHours });
        setMessage("Registration Successful!");

        setTimeout(() => {
          navigate("/");
        }, 1000);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Registration failed");
      }
    } catch {
      setMessage("Network error");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "#f0f2f5",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <form
        onSubmit={handleRegister}
        style={{
          backgroundColor: "#fff",
          padding: "40px",
          borderRadius: "15px",
          boxShadow: "0 8px 20px rgba(0,0,0,0.2)",
          width: "350px",
          textAlign: "center",
        }}
      >
        <h2 style={{ marginBottom: "20px", color: "#28a745" }}>Register</h2>

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "15px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none",
          }}
          required
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "15px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none",
          }}
          required
        />

        <input
          type="number"
          value={availableHours}
          min={0.5}
          step={0.5}
          onChange={(e) => setAvailableHours(parseFloat(e.target.value))}
          placeholder="Available Hours Per Day"
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "20px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none",
          }}
          required
        />

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "#28a745",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Register
        </button>
        {message && (
          <p style={{ marginTop: "15px", color: "#007bff", fontWeight: "bold" }}>
            {message}
          </p>
        )}
      </form>
    </div>
  );
}
