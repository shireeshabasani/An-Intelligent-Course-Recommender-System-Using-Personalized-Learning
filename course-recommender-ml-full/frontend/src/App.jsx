import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import Register from "./components/Register";
import SearchResults from "./components/SearchResults";
import Dashboard from "./components/Dashboard";
import SkillGapPage from "./components/SkillGapPage";
import Achievements from "./components/Achievements"; 
import QuizPage from "./components/QuizPage";
import Journey from "./components/Journey"; 
import JourneyQuiz from "./components/JourneyQuiz";

function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home user={user} onLogout={handleLogout} />} />
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/register" element={<Register onRegister={setUser} />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={user ? <Dashboard user={user} /> : <Navigate to="/login" />} />
        <Route path="/search-results" element={user ? <SearchResults user={user} /> : <Navigate to="/login" />} />
        <Route path="/skill-gap" element={user ? <SkillGapPage email={user.email} /> : <Navigate to="/login" />} />
        <Route path="/achievements" element={user ? <Achievements user={user} /> : <Navigate to="/login" />} />
        
        {/* Roadmap & Level Locking Routes */}
        <Route path="/journey" element={user ? <Journey user={user} /> : <Navigate to="/login" />} />
         {/* Find this line in your App.js and update it */}
        <Route path="/journey-quiz/:levelId" element={user ? <JourneyQuiz user={user} setUser={setUser} /> : <Navigate to="/login" />} />          
        
        {/* Dashboard Quiz Routing */}
        <Route path="/quiz/:courseId/:quizNum" element={user ? <QuizPage user={user} /> : <Navigate to="/login" />} />
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;