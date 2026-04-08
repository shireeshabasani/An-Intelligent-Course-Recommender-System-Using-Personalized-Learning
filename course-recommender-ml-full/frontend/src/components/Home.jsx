import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Home({ user, onLogout }) {
  const [query, setQuery] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  const displayName = user?.name || (user?.email ? user.email.split('@')[0] : "Guest");
  const userEmail = user?.email || "";

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim() !== "") {
      navigate(`/search-results?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div style={containerStyle}>
      <nav style={navbarStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ fontWeight: 'bold', color: '#333', cursor: 'pointer' }} onClick={() => navigate("/")}>Priority Pass</span>
        </div>

        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {!user ? (
            <div style={{ display: 'flex', gap: '10px' }}>
              <Link to="/login" style={authBtnStyle('#007bff')}>Login</Link>
              <Link to="/register" style={authBtnStyle('#28a745')}>Register</Link>
            </div>
          ) : (
            <div style={{ position: "relative" }} ref={dropdownRef}>
              <div onClick={() => setDropdownOpen(!dropdownOpen)} style={profileTriggerStyle}>
                <div style={avatarStyle}>{displayName.charAt(0).toUpperCase()}</div>
                <span style={{ fontSize: '10px', color: '#03a9f4' }}>{dropdownOpen ? '▲' : '▼'}</span>
              </div>

              {dropdownOpen && (
                <div style={dropdownCardStyle}>
                  <div style={{ padding: '15px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 'bold', textTransform: 'capitalize' }}>{displayName}</span>
                      <span style={{ color: '#03a9f4' }}>✔️</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#777' }}>{userEmail}</div>
                  </div>
                  
                  <div style={dividerStyle} />
                  
                  {/* RESTORED: "Know More" Option Section */}
                  <div style={{ padding: '12px 15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <span style={{ color: '#ffc107' }}>★</span>
                      <span style={{ fontWeight: 'bold' }}>5</span>
                    </div>
                    <span 
                      style={knowMoreLink} 
                      onClick={() => { navigate("/journey"); setDropdownOpen(false); }}
                    >
                      Know More ➔
                    </span>
                  </div>

                  <div style={dividerStyle} />
                  
                  <div style={{ padding: '5px 0' }}>
                    <button onClick={() => { navigate("/dashboard"); setDropdownOpen(false); }} style={menuBtnStyle}>Dashboard</button>
                    <button onClick={() => { navigate("/skill-gap"); setDropdownOpen(false); }} style={menuBtnStyle}>Skill Gap Analysis</button>
                    
                    <button 
                      onClick={() => { navigate("/achievements"); setDropdownOpen(false); }} 
                      style={{...menuBtnStyle, color: '#38A169', fontWeight: 'bold'}}
                    >
                      🎓 Academic Achievements
                    </button>
                    
                    <div style={dividerStyle} />
                    <button onClick={() => { onLogout(); setDropdownOpen(false); }} style={{...menuBtnStyle, color: 'red'}}>Logout</button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section and Footer remain the same */}
      <div style={heroSectionStyle}>
        <h1 style={heroTitleStyle}>Course Recommender</h1>
        <p style={{ fontSize: "1.2rem", marginBottom: "30px" }}>Discover the best courses for your skills and goals</p>
        
        <button onClick={() => navigate("/skill-gap")} style={skillGapBtnStyle}>
          Skill Gap Analysis
        </button>

        <form onSubmit={handleSearch} style={searchFormStyle}>
          <input 
            type="text" 
            placeholder="Search courses or skills..." 
            style={searchInputStyle} 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" style={searchSubmitBtnStyle}>Search</button>
        </form>
      </div>

      <footer style={footerStyle}>
        <p>© 2026 Course Recommender Platform</p>
      </footer>
    </div>
  );
}

// Styles
const containerStyle = { minHeight: "100vh", display: "flex", flexDirection: "column", fontFamily: "Arial, sans-serif" };
const navbarStyle = { display: 'flex', justifyContent: 'space-between', padding: '10px 40px', backgroundColor: '#fff', borderBottom: '1px solid #eee', alignItems: 'center' };
const authBtnStyle = (bgColor) => ({ padding: "8px 16px", backgroundColor: bgColor, borderRadius: "4px", textDecoration: "none", color: "#fff", fontWeight: "bold", fontSize: "14px" });
const profileTriggerStyle = { display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', padding: '4px 8px', borderRadius: '4px', backgroundColor: '#f0faff' };
const avatarStyle = { width: '30px', height: '30px', borderRadius: '50%', backgroundColor: '#03a9f4', color: '#fff', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold' };
const dropdownCardStyle = { position: 'absolute', right: 0, top: '45px', width: '250px', backgroundColor: '#fff', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', borderRadius: '8px', zIndex: 100 };
const dividerStyle = { height: '1px', backgroundColor: '#eee', width: '100%' };
const knowMoreLink = { color: '#03a9f4', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold' };
const menuBtnStyle = { width: '100%', padding: '12px 15px', textAlign: 'left', border: 'none', background: 'none', cursor: 'pointer', fontSize: '14px' };
const heroSectionStyle = { flex: 1, padding: "80px 20px", textAlign: "center", backgroundImage: 'linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url(https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1950&q=80)', backgroundSize: 'cover', color: "#fff" };
const heroTitleStyle = { fontSize: "3.5rem", color: "#ffeb3b", marginBottom: '10px' };
const skillGapBtnStyle = { padding: '12px 30px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', margin: '20px 0' };
const searchFormStyle = { display: "flex", width: "90%", maxWidth: "600px", margin: "20px auto" };
const searchInputStyle = { flex: 1, padding: "15px", borderRadius: "5px 0 0 5px", border: "none", outline: "none", fontSize: "1rem" };
const searchSubmitBtnStyle = { padding: "15px 30px", backgroundColor: "#ff6600", color: "#fff", border: "none", borderRadius: "0 5px 5px 0", cursor: "pointer", fontWeight: "bold" };
const footerStyle = { width: "100%", padding: "20px", textAlign: "center", backgroundColor: "rgba(0,0,0,0.8)", color: "#fff" };