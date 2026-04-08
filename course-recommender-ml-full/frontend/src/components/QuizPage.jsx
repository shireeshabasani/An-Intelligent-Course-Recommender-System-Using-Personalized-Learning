import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

const QuizPage = ({ user }) => {
  const { courseId, quizNum } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  // 1. Initialize Page: Load Quiz and Check Completion Status
  useEffect(() => {
    if (!courseId || courseId === "undefined") {
      console.error("Course ID is missing or undefined.");
      setLoading(false);
      return;
    }

    const initQuiz = async () => {
      try {
        setLoading(true);
        // Fetch questions
        const qRes = await fetch(`http://localhost:8000/quiz/${courseId}/${quizNum}`);
        if (!qRes.ok) throw new Error("Quiz not found");
        const qData = await qRes.json();
        setQuiz(qData);

        // Check if already completed (Persistence)
        const sRes = await fetch(`http://localhost:8000/quiz/status?email=${user.email}&course_id=${courseId}&quiz_num=${quizNum}`);
        if (sRes.ok) {
          const sData = await sRes.json();
          if (sData.completed) {
            setResult(sData.previous_result);
          }
        }
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setLoading(false);
      }
    };
    initQuiz();
  }, [courseId, quizNum, user.email]);

  // 2. Handle Submission
  const handleSubmit = async () => {
    const answersArray = quiz.questions.map((_, i) => answers[i] ?? -1);
    
    try {
      const res = await fetch("http://localhost:8000/quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email: user.email, 
          course_id: courseId, 
          quiz_number: parseInt(quizNum), 
          answers: answersArray 
        })
      });

      if (!res.ok) throw new Error("Submission failed");
      
      const data = await res.json();
      // 'data' now includes the 'details' array from the updated backend
      setResult(data); 
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      alert("Failed to submit. Please check your connection.");
    }
  };

  if (loading) return <div style={msgStyle}>Loading Assessment...</div>;
  
  if (!quiz) return (
    <div style={{...msgStyle, color: "#E53E3E"}}>
      <h3>Error: Quiz or Course ID not found.</h3>
      <button onClick={() => navigate("/dashboard")} style={{...returnBtnStyle, width: "auto", padding: "10px 20px"}}>
        Back to Dashboard
      </button>
    </div>
  );

  return (
    <div style={{ maxWidth: "800px", margin: "2rem auto", padding: "20px", fontFamily: "'Segoe UI', Tahoma, sans-serif" }}>
      
      {/* HEADER */}
      <div style={{ borderBottom: "3px solid #38A169", marginBottom: "30px", paddingBottom: "10px" }}>
        <h2 style={{ textTransform: "uppercase", color: "#2D3748", margin: 0 }}>
          Level {quizNum}: {quiz.course_title || courseId.replace(/-/g, ' ')}
        </h2>
      </div>

   {/* PERFORMANCE SUMMARY */}

{result && (

<div style={{

textAlign: "center", padding: "30px", marginBottom: "30px", borderRadius: "15px",

backgroundColor: result.passed ? "#F0FFF4" : "#FFF5F5",

border: `2px solid ${result.passed ? "#38A169" : "#E53E3E"}`,

boxShadow: "0 4px 12px rgba(0,0,0,0.05)"

}}>

<h2 style={{ color: result.passed ? "#2F855A" : "#C53030", margin: 0 }}>

{result.passed ? "🎉 Level Mastered!" : "⚠️ Review Required"}

</h2>

<div style={{ fontSize: "1.8rem", margin: "15px 0", color: "#2D3748" }}>

Score: <strong>{result.score} / {result.total}</strong>

</div>

<p style={{ fontSize: "1.1rem", color: "#4A5568", margin: 0 }}>

Success Rate: <strong>{result.percentage}%</strong>

{result.passed ? " (Pass)" : " (Below 80% Threshold)"}

</p>

</div>

)} 

      {/* QUESTIONS LIST */}
      {quiz.questions.map((q, idx) => {
        // Accessing the specific question feedback from the results details
        const review = result?.details?.[idx]; 
        
        return (
          <div key={idx} style={questionBoxStyle}>
            <p style={{ fontSize: "1.1rem", fontWeight: "600", color: "#2D3748" }}>
              {idx + 1}. {q.question}
            </p>
            
            {q.options.map((opt, oIdx) => {
              // 1. Check if user selected this option
              const isSelected = result ? review?.user_answer === oIdx : answers[idx] === oIdx;
              
              // 2. Check if this option is the correct answer
              const isCorrect = result ? review?.correct_answer === oIdx : false;

              // 3. Styling Logic
              let bgColor = "transparent";
              let borderColor = "#edf2f7";
              
              if (result) {
                if (isCorrect) {
                  bgColor = "#F0FFF4"; // Correct answers always green
                  borderColor = "#38A169";
                } else if (isSelected && !isCorrect) {
                  bgColor = "#FFF5F5"; // Selected wrong answers red
                  borderColor = "#E53E3E";
                }
              } else if (isSelected) {
                bgColor = "#EBF8FF"; // Selection highlight
                borderColor = "#3182CE";
              }

              return (
                <label key={oIdx} style={{ ...optionLabelStyle, backgroundColor: bgColor, borderColor: borderColor }}>
                  <input 
                    type="radio" 
                    name={`q-${idx}`} 
                    disabled={!!result} 
                    style={{ marginRight: "12px", width: "18px", height: "18px" }}
                    checked={isSelected}
                    onChange={() => setAnswers({ ...answers, [idx]: oIdx })} 
                  /> 
                  <span style={{ color: "#4A5568", flex: 1 }}>{opt}</span>
                  
                  {/* FEEDBACK TAGS */}
                  {result && isCorrect && <span style={tagStyle("#38A169")}>✅ Correct</span>}
                  {result && isSelected && !isCorrect && <span style={tagStyle("#E53E3E")}>❌ Your Choice</span>}
                </label>
              );
            })}
          </div>
        );
      })}

      {/* FOOTER ACTIONS */}
      <div style={{ marginTop: "40px" }}>
        {!result ? (
          <button onClick={handleSubmit} style={submitBtnStyle}>
            Submit Final Answers
          </button>
        ) : (
          <div style={{ display: "flex", gap: "15px" }}>
             <button onClick={() => navigate("/dashboard")} style={returnBtnStyle}>
              Return to Dashboard
            </button>
            {/* Optional Retry logic if they failed */}
            {!result.passed && (
                <button 
                  onClick={() => { setResult(null); setAnswers({}); }} 
                  style={{ ...returnBtnStyle, backgroundColor: "#718096" }}
                >
                  Try Again
                </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// --- STYLES ---
const msgStyle = { textAlign: "center", padding: "100px", fontSize: "1.2rem", fontFamily: "sans-serif" };
const questionBoxStyle = { marginBottom: "20px", padding: "20px", backgroundColor: "#fff", border: "1px solid #e2e8f0", borderRadius: "12px", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" };
const optionLabelStyle = { display: "flex", alignItems: "center", margin: "10px 0", cursor: "pointer", padding: "12px", borderRadius: "8px", border: "1px solid", transition: "0.2s ease" };
const tagStyle = (color) => ({ color: color, fontWeight: "bold", fontSize: "0.85rem", marginLeft: "10px" });
const submitBtnStyle = { padding: "15px", backgroundColor: "#38A169", color: "white", border: "none", borderRadius: "8px", cursor: "pointer", width: "100%", fontWeight: "bold", fontSize: "1.1rem", boxShadow: "0 4px 6px rgba(56, 161, 105, 0.2)" };
const returnBtnStyle = { ...submitBtnStyle, backgroundColor: "#3182CE", flex: 1 };

export default QuizPage;