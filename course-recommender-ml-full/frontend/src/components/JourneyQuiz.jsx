import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const JourneyQuiz = ({ user, setUser }) => {
  const { levelId } = useParams(); 
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!user?.email) return;

    fetch(`http://localhost:8000/quiz/roadmap/${levelId}?email=${user.email}`)
      .then(res => res.json())
      .then(data => {
        console.log("BACKEND DATA RECEIVED:", data); // DEBUG HERE
        setQuiz(data);
        
        if (data.previous_result) {
          setResult({
            percentage: data.previous_result.percentage,
            passed: data.previous_result.passed,
            details: data.questions.map((q, i) => ({
              question: q.question,
              options: q.options,
              user_answer: data.previous_result.answers[i],
              correct_answer: q.answer, // Check if this exists in the console log!
              is_correct: data.previous_result.answers[i] === q.answer
            }))
          });
        }
      });
}, [levelId, user?.email]);

const handleSubmit = async () => {
  const answerArray = quiz.questions.map((_, i) => answers[i] ?? -1);

  try {
    const response = await fetch('http://localhost:8000/quiz/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: user.email,
        course_id: "roadmap", // This tells the backend to use the 40% threshold
        quiz_number: parseInt(levelId),
        answers: answerArray
      })
    });
    
    if (!response.ok) throw new Error("Server rejected submission");
    const data = await response.json();

    // Use data.passed from backend (which is 40% for roadmap)
    const finalResult = {
      ...data,
      details: quiz.questions.map((q, i) => ({
        question: q.question,
        options: q.options,
        user_answer: answerArray[i],
        correct_answer: q.answer,
        is_correct: answerArray[i] === q.answer
      }))
    };
    
    setResult(finalResult);

    // If backend confirmed a pass, sync the User state to unlock the next map node
    if (data.passed) {
      const userRes = await fetch(`http://localhost:8000/users/${user.email}`);
      if (userRes.ok) {
          const freshUser = await userRes.json();
          setUser(freshUser); 
          localStorage.setItem("user", JSON.stringify(freshUser));
      }
    }
  } catch (error) {
    console.error(error);
    alert("Submission failed. Ensure your backend is running.");
  }
};

  if (!quiz) return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading Level...</div>;

  return (
    <div className="roadmap-quiz-container">
      <div className="quiz-card">
        <div className="quiz-header">
          <h2>LEVEL {levelId}: {quiz.course_title}</h2>
          <div className="status-chip">{result ? "Completed" : "In Progress"}</div>
        </div>

        {!result ? (
          <div className="quiz-body">
            {quiz.questions.map((q, idx) => (
              <div key={idx} className="question-item">
                <p className="question-text">{idx + 1}. {q.question}</p>
                <div className="options-grid">
                  {q.options.map((opt, i) => (
                    <button 
                      key={i} 
                      className={`opt-btn ${answers[idx] === i ? 'active' : ''}`}
                      onClick={() => setAnswers({...answers, [idx]: i})}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <button 
              onClick={handleSubmit} 
              className="submit-action-btn"
              disabled={Object.keys(answers).length < quiz.questions.length}
            >
              Finish Level
            </button>
          </div>
        ) : (
          <div className="review-body">
            <div className={`result-banner ${result.passed ? 'success' : 'fail'}`}>
              <h1>{result.percentage}%</h1>
              <p>{result.passed ? "Level Passed!" : "Try again to unlock the next level."}</p>
            </div>
            
            <div className="review-scroll">
  {result.details?.map((d, i) => (
    <div key={i} className={`rev-card ${d.is_correct ? 'right' : 'wrong'}`}>
      <p><strong>{i+1}. {d.question}</strong></p>
      {/* Show what the user selected */}
      <p className="user-ans">Your Answer: {d.options[d.user_answer] || "None"}</p>
      {/* The "Correct Answer" line has been removed to clean up the UI */}
    </div>
  ))}
</div>

{/* If the user failed, show a Try Again button to reset the quiz state */}
{!result.passed && (
  <button 
    onClick={() => {
      setResult(null); 
      setAnswers({});
    }} 
    className="retake-btn"
  >
    Try Again
  </button>
)}

<button onClick={() => navigate('/journey')} className="journey-return-btn">
  Go to Journey Map
</button>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .roadmap-quiz-container { padding: 40px 20px; background: #f0f2f5; min-height: 100vh; font-family: 'Segoe UI', sans-serif; }
        .quiz-card { max-width: 650px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }
        .quiz-header { padding: 20px 30px; background: #1f2937; color: white; display: flex; justify-content: space-between; align-items: center; }
        .status-chip { background: #4b5563; padding: 4px 12px; border-radius: 12px; font-size: 12px; }
        .quiz-body, .review-body { padding: 30px; }
        .question-item { margin-bottom: 25px; }
        .question-text { font-weight: 600; font-size: 17px; margin-bottom: 15px; }
        .options-grid { display: grid; gap: 10px; }
        .opt-btn { padding: 14px; text-align: left; border: 2px solid #e5e7eb; border-radius: 12px; background: white; cursor: pointer; transition: 0.2s; }
        .opt-btn:hover { border-color: #3b82f6; }
        .opt-btn.active { background: #eff6ff; border-color: #3b82f6; font-weight: 600; color: #1d4ed8; }
        .submit-action-btn { width: 100%; padding: 16px; background: #10b981; color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        .result-banner { text-align: center; padding: 30px; border-radius: 15px; margin-bottom: 25px; }
        .result-banner.success { background: #dcfce7; color: #166534; }
        .result-banner.fail { background: #fee2e2; color: #991b1b; }
        .rev-card { padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 5px solid; }
        .rev-card.right { background: #f0fdf4; border-color: #22c55e; }
        .rev-card.wrong { background: #fef2f2; border-color: #ef4444; }
        .corr-ans { color: #059669; font-weight: 600; margin-top: 5px; }
        .journey-return-btn { width: 100%; padding: 16px; background: #3b82f6; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; }
      `}} />
    </div>
  );
};

export default JourneyQuiz;