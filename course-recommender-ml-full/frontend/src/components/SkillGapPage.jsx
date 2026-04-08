import React, { useState, useEffect } from "react";
import axios from "axios";

const allSkills = [
  "Python","HTML","CSS","JavaScript","React","Node.js","Java","SQL",
  "Machine Learning","Deep Learning","Docker","Kubernetes","AWS",
  "GCP","Azure","Cloud Computing","API","REST API","DevOps",
  "Database","MongoDB","PostgreSQL","Frontend","Backend","Django","express.js","next.js","angular"
];

const roles = [
  "Data Scientist",
  "Web Developer",
  "ML Engineer",
  "DevOps Engineer",
  "Cloud Architect",
  "Frontend Developer",
  "Backend Developer",
  "Database Administrator"
];

const SkillGapPage = ({ email }) => {
  const [userSkills,setUserSkills] = useState([]);
  const [skillsInput,setSkillsInput] = useState("");
  const [filteredSkills,setFilteredSkills] = useState([]);
  const [skillsSaved,setSkillsSaved] = useState(false);

  const [role,setRole] = useState("");
  const [data,setData] = useState(null);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState(null);

  const API = "http://127.0.0.1:8000";

  // ---------------- LOAD USER SKILLS ----------------
  useEffect(()=>{
    async function loadSkills(){
      try{
        const res = await axios.get(`${API}/users/${encodeURIComponent(email)}`);
        const skills = res.data.skills || [];
        if(skills.length>0){
          setUserSkills(skills);
          setSkillsSaved(true);
        }
      }catch(err){ console.log(err); }
    }
    if(email){ loadSkills(); }
  },[email]);

  // ---------------- FILTER SKILLS (AUTOCOMPLETE) ----------------
  useEffect(()=>{
    const q = skillsInput.toLowerCase().trim();
    if(q===""){ setFilteredSkills([]); return; }

    const filtered = allSkills.filter(
      s => s.toLowerCase().startsWith(q) &&
           !userSkills.some(us => us.toLowerCase() === s.toLowerCase())
    );

    setFilteredSkills(filtered);
  },[skillsInput,userSkills]);

  // ---------------- ADD SKILL ----------------
  const addSkill=(skill)=>{
    if(!userSkills.some(us => us.toLowerCase() === skill.toLowerCase())){
      setUserSkills([...userSkills, skill]);
    }
    setSkillsInput("");
    setFilteredSkills([]);
  };

  // ---------------- REMOVE SKILL ----------------
  const removeSkill=(skill)=>{
    setUserSkills(userSkills.filter(s => s.toLowerCase() !== skill.toLowerCase()));
  };

  // ---------------- SAVE SKILLS ----------------
  const saveSkills=async()=>{
    if(userSkills.length===0){ alert("Add at least one skill"); return; }
    try{
      await axios.put(`${API}/users/${encodeURIComponent(email)}/skills`, userSkills);
      setSkillsSaved(true);
    }catch(err){ alert("Failed to save skills"); }
  };

  // ---------------- FETCH SKILL GAP ----------------
  const fetchSkillGap=async()=>{
    if(!role) return;
    setLoading(true);
    try{
      const res = await axios.get(`${API}/users/${encodeURIComponent(email)}/skill-gap`, { params:{role} });
      setData(res.data);
      setError(null);
    }catch(err){
      setError("Skill gap fetch failed");
      setData(null);
    }
    setLoading(false);
  };

  // ---------------- SKILL EDIT SCREEN ----------------
  if(!skillsSaved){
    return(
      <div style={{maxWidth:600,margin:"40px auto"}}>
        <h2>Add Your Skills</h2>
        <input
          type="text"
          value={skillsInput}
          onChange={(e)=>setSkillsInput(e.target.value)}
          placeholder="Type skill"
          style={{width:"100%",padding:10}}
        />
        {filteredSkills.length>0 && (
          <ul style={{border:"1px solid #ccc"}}>
            {filteredSkills.map(s=>(
              <li key={s} onClick={()=>addSkill(s)} style={{padding:8,cursor:"pointer"}}>{s}</li>
            ))}
          </ul>
        )}
        <div style={{marginTop:15}}>
          {userSkills.map(s=>(
            <span key={s} style={{background:"#007bff", color:"white", padding:"5px 10px", margin:5, borderRadius:20}}>
              {s}
              <button onClick={()=>removeSkill(s)} style={{marginLeft:5, border:"none", background:"transparent", color:"white", cursor:"pointer"}}>×</button>
            </span>
          ))}
        </div>
        <button onClick={saveSkills} style={{marginTop:20, padding:"10px 20px", background:"green", color:"white", border:"none"}}>Save Skills</button>
      </div>
    );
  }

  // ---------------- SKILL GAP SCREEN ----------------
  return(
    <div style={{maxWidth:700,margin:"40px auto"}}>
      <h2>Skill Gap Analysis</h2>
      <p>
        <b>Your Skills:</b> {userSkills.join(", ")}
        <button onClick={()=>{setSkillsSaved(false);setData(null);}} style={{marginLeft:15}}>Edit Skills</button>
      </p>
      <select value={role} onChange={(e)=>setRole(e.target.value)} style={{width:"100%",padding:10}}>
        <option value="">Select Role</option>
        {roles.map(r=><option key={r}>{r}</option>)}
      </select>
      <button onClick={fetchSkillGap} disabled={!role || loading} style={{marginTop:15,padding:10,width:"100%",background:"#007bff",color:"white",border:"none"}}>
        {loading?"Checking...":"Check Skill Gap"}
      </button>
      {error && <p style={{color:"red"}}>{error}</p>}
      {data && (
        <div style={{marginTop:25}}>
          <h3>{role}</h3>
          <p><b>Required Skills:</b> {(data.required_skills || []).join(", ") || "None"}</p>
          <p><b>Your Matching Skills:</b> {(data.existing_skills || []).join(", ") || "None"}</p>
          <p><b>Missing Skills:</b> {(data.missing_skills || []).join(", ") || "None"}</p>
          {data.recommended_courses && data.recommended_courses.length>0 &&(
            <>
              <h4>Recommended Courses</h4>
              <ul>
                {data.recommended_courses.map((c,i)=>(
                  <li key={i}><a href={c.url} target="_blank" rel="noreferrer">{c.course_title}</a></li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default SkillGapPage;