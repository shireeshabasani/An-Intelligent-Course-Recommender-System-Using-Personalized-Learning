import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import Register from "./components/Register";
import SearchResults from "./components/SearchResults";
import Dashboard from "./components/Dashboard";
import SkillGapPage from "./components/SkillGapPage";
import Achievements from "./components/Achievements"; // <-- NEW IMPORT

function App() {
  const [user, setUser] = useState(null); // stores logged-in user info

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/login" element={<Login onLogin={setUser} />} />
        <Route path="/register" element={<Register onRegister={setUser} />} />
        <Route
          path="/search-results"
          element={user ? <SearchResults user={user} /> : <Navigate to="/login" />}
        />
        <Route
          path="/dashboard"
          element={user ? <Dashboard user={user} /> : <Navigate to="/login" />}
        />
        <Route
          path="/skill-gap"
          element={user ? <SkillGapPage email={user.email} /> : <Navigate to="/login" />}
        />
        {/* ACHIEVEMENTS ROUTE ADDED */}
        <Route
          path="/achievements"
          element={user ? <Achievements email={user.email} /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}

export default App;
