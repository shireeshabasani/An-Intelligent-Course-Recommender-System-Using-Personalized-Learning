import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!email || !password) {
      setMessage("Please enter valid credentials");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(data.user);
        setMessage("Login Successful!");

        setTimeout(() => {
          navigate("/");
        }, 1000);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed");
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
        onSubmit={handleLogin}
        style={{
          backgroundColor: "#fff",
          padding: "40px",
          borderRadius: "15px",
          boxShadow: "0 8px 20px rgba(0,0,0,0.2)",
          width: "350px",
          textAlign: "center",
        }}
      >
        <h2 style={{ marginBottom: "20px", color: "#007bff" }}>Login</h2>
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
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Login
        </button>
        {message && (
          <p style={{ marginTop: "15px", color: "#28a745", fontWeight: "bold" }}>
            {message}
          </p>
        )}
        <p style={{ marginTop: "15px" }}>
          New user?{" "}
          <span
            style={{ color: "blue", cursor: "pointer", textDecoration: "underline" }}
            onClick={() => navigate("/register")}
          >
            Register here
          </span>
        </p>
      </form>
    </div>
  );
}
